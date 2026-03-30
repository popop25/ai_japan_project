from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel, Field

from .atlassian import (
    AtlassianClient,
    AtlassianServiceClient,
    JIRA_STATUS_TARGETS,
    is_task_issue_type_name,
    join_atlassian_url,
    page_url,
)
from .factory import AtlassianClientFactory, build_project_service
from .models import IngestCriticRequest, IngestPMRequest, Status
from .paths import (
    ARTIFACTS_DIR,
    CONTEXT_MARKDOWN_PATH,
    CONTEXT_YAML_PATH,
    CRITIC_SKILL_PATH,
    PM_SKILL_PATH,
    RUNS_DIR,
    SMOKE_RECEIPTS_DIR,
    TASKS_DIR,
)
from .settings import AppMode, AppSettings, AtlassianSettings

SMOKE_PREFIX = "[AJP Smoke]"

PM_SMOKE_DOCUMENT = """# 배경
- 일본 리테일 고객사의 업무 실증을 위한 스모크 테스트입니다.

# 목표
- 요구사항 정의서 초안을 생성 가능한지 확인합니다.

# 기능 요구사항
- 프로젝트 컨텍스트를 읽을 수 있어야 합니다.
- PM 산출물을 저장할 수 있어야 합니다.
- Critic 리뷰 결과를 반영할 수 있어야 합니다.

# 비기능 요구사항
- Atlassian Cloud와 연결되어야 합니다.
- 결과물은 추적 가능해야 합니다.

# 오픈 이슈
- 실제 운영 워크플로 상태명 검증

# 다음 액션
- Critic 리뷰 수행
"""

CRITIC_SMOKE_DOCUMENT = """---
verdict: approve
summary: Smoke test review approved.
missing_items:
  - none
recommended_changes:
  - Validate production workflow names before broader rollout.
---
The draft is sufficient for an end-to-end integration smoke test.
"""


class ReadinessCheck(BaseModel):
    name: str
    status: Literal["pass", "warn", "fail"]
    detail: str
    link: str | None = None


class ReadinessReport(BaseModel):
    mode: AppMode
    overall_status: Literal["pass", "warn", "fail"]
    summary: str
    checks: list[ReadinessCheck] = Field(default_factory=list)


class SmokeReceipt(BaseModel):
    prefix: str
    created_at: str
    task_id: str
    task_title: str
    jira_issue_key: str
    jira_issue_url: str
    pm_packet_path: str
    critic_packet_path: str
    pm_artifact_url: str
    critic_review_url: str
    final_status: str
    receipt_path: str | None = None


class CleanupTarget(BaseModel):
    kind: Literal["jira_issue", "confluence_page", "local_file", "receipt"]
    identifier: str
    label: str
    status: Literal["planned", "deleted", "missing", "failed"] = "planned"
    url: str | None = None
    detail: str | None = None


class CleanupPlan(BaseModel):
    prefix: str
    apply: bool
    summary: str
    targets: list[CleanupTarget] = Field(default_factory=list)


def load_app_settings(*, mode: AppMode | None = None, dotenv_path: Path | None = None) -> AppSettings:
    settings = AppSettings.from_env(dotenv_path=dotenv_path)
    if mode is None:
        return settings
    return settings.model_copy(update={"mode": mode})


def build_readiness_report(
    settings: AppSettings | None = None,
    *,
    client_factory: AtlassianClientFactory | None = None,
) -> ReadinessReport:
    settings = settings or AppSettings.from_env()
    if settings.mode == AppMode.LOCAL:
        checks = _local_readiness_checks()
        return ReadinessReport(
            mode=settings.mode,
            overall_status=_overall_status(checks),
            summary=_build_summary(checks),
            checks=checks,
        )

    checks: list[ReadinessCheck] = []
    try:
        atlassian_settings = settings.atlassian_settings()
    except ValueError as exc:
        checks.append(ReadinessCheck(name="Atlassian config", status="fail", detail=str(exc)))
        return ReadinessReport(
            mode=settings.mode,
            overall_status="fail",
            summary=_build_summary(checks),
            checks=checks,
        )

    checks.append(
        ReadinessCheck(
            name="Atlassian config",
            status="pass",
            detail="Atlassian mode configuration loaded from OS env or .env.",
        )
    )

    client_factory = client_factory or AtlassianClient.from_settings
    client = client_factory(atlassian_settings)
    checks.extend(_atlassian_readiness_checks(client, atlassian_settings))
    return ReadinessReport(
        mode=settings.mode,
        overall_status=_overall_status(checks),
        summary=_build_summary(checks),
        checks=checks,
    )


def render_readiness_report(report: ReadinessReport) -> str:
    lines = [
        f"AI Japan Project readiness ({report.mode.value})",
        f"Overall: {report.overall_status.upper()} - {report.summary}",
        "",
    ]
    for check in report.checks:
        line = f"[{check.status.upper()}] {check.name}: {check.detail}"
        if check.link:
            line += f" ({check.link})"
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def run_atlassian_smoke(
    settings: AppSettings | None = None,
    *,
    prefix: str = SMOKE_PREFIX,
    receipts_dir: Path = SMOKE_RECEIPTS_DIR,
) -> SmokeReceipt:
    settings = settings or AppSettings.from_env()
    if settings.mode != AppMode.ATLASSIAN:
        raise ValueError("Smoke runs require atlassian mode. Set AJP_MODE=atlassian or override the mode in the script.")

    service = build_project_service(settings)
    context, _ = service.get_context()
    service.save_context(context)

    stamp = _utc_now().replace(":", "").replace("-", "")
    task_title = f"{prefix} Requirements Draft {stamp}"
    detail = service.create_requirements_task(task_title)
    detail = service.dispatch_pm(detail.task.id)
    if detail.pm_packet is None:
        raise ValueError("PM packet was not created during smoke run.")

    detail = service.ingest_pm(
        detail.task.id,
        IngestPMRequest(content=PM_SMOKE_DOCUMENT, title=f"{prefix} PM Draft {stamp}"),
    )
    pm_artifact = next((artifact for artifact in detail.artifacts if artifact.kind == "pm_output"), None)
    if pm_artifact is None:
        raise ValueError("PM artifact was not created during smoke run.")

    detail = service.dispatch_critic(detail.task.id)
    if detail.critic_packet is None:
        raise ValueError("Critic packet was not created during smoke run.")

    detail = service.ingest_critic(detail.task.id, IngestCriticRequest(review_markdown=CRITIC_SMOKE_DOCUMENT))
    critic_artifact = next((artifact for artifact in detail.artifacts if artifact.kind == "critic_review"), None)
    if critic_artifact is None:
        raise ValueError("Critic review artifact was not created during smoke run.")

    receipt = SmokeReceipt(
        prefix=prefix,
        created_at=_utc_now(),
        task_id=detail.task.id,
        task_title=task_title,
        jira_issue_key=detail.task.refs.get("jira_issue_key", ""),
        jira_issue_url=detail.task.refs.get("jira_issue_url", ""),
        pm_packet_path=str(_resolve_local_path(detail.pm_packet.path)),
        critic_packet_path=str(_resolve_local_path(detail.critic_packet.path)),
        pm_artifact_url=pm_artifact.path,
        critic_review_url=critic_artifact.path,
        final_status=detail.task.status.value,
    )
    receipt_path = save_smoke_receipt(receipt, receipts_dir=receipts_dir)
    return receipt.model_copy(update={"receipt_path": str(receipt_path)})


def save_smoke_receipt(receipt: SmokeReceipt, *, receipts_dir: Path = SMOKE_RECEIPTS_DIR) -> Path:
    receipts_dir.mkdir(parents=True, exist_ok=True)
    path = receipts_dir / f"smoke_{receipt.created_at.replace(':', '').replace('-', '')}_{receipt.task_id}.json"
    path.write_text(receipt.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_smoke_receipts(*, prefix: str | None = None, receipts_dir: Path = SMOKE_RECEIPTS_DIR) -> list[SmokeReceipt]:
    receipts: list[SmokeReceipt] = []
    if not receipts_dir.exists():
        return receipts
    for path in receipts_dir.glob("smoke_*.json"):
        receipt = SmokeReceipt.model_validate_json(path.read_text(encoding="utf-8"))
        receipt = receipt.model_copy(update={"receipt_path": str(path)})
        if prefix and receipt.prefix != prefix:
            continue
        receipts.append(receipt)
    receipts.sort(key=lambda item: item.created_at, reverse=True)
    return receipts


def cleanup_smoke_receipts(
    settings: AppSettings | None = None,
    *,
    prefix: str = SMOKE_PREFIX,
    receipts_dir: Path = SMOKE_RECEIPTS_DIR,
    apply: bool = False,
    client_factory: AtlassianClientFactory | None = None,
) -> CleanupPlan:
    receipts = load_smoke_receipts(prefix=prefix, receipts_dir=receipts_dir)
    if not receipts:
        return CleanupPlan(prefix=prefix, apply=apply, summary="No smoke receipts found.", targets=[])

    targets = _build_cleanup_targets(receipts)
    if not apply:
        return CleanupPlan(prefix=prefix, apply=False, summary=_build_cleanup_summary(targets, apply=False), targets=targets)

    settings = settings or AppSettings.from_env()
    if settings.mode != AppMode.ATLASSIAN:
        raise ValueError("Cleanup apply requires atlassian mode so Jira and Confluence resources can be deleted.")

    client_factory = client_factory or AtlassianClient.from_settings
    client = client_factory(settings.atlassian_settings())
    for target in targets:
        try:
            if target.kind == "jira_issue":
                client.jira_json("DELETE", f"/rest/api/3/issue/{target.identifier}?deleteSubtasks=true")
                target.status = "deleted"
                target.detail = "Deleted Jira issue."
            elif target.kind == "confluence_page":
                client.confluence_json("DELETE", f"/rest/api/content/{target.identifier}")
                target.status = "deleted"
                target.detail = "Deleted Confluence page."
            else:
                path = Path(target.identifier)
                if path.exists():
                    path.unlink()
                    target.status = "deleted"
                    target.detail = "Removed local file."
                else:
                    target.status = "missing"
                    target.detail = "Local file was already missing."
        except Exception as exc:  # noqa: BLE001 - cleanup should continue collecting results.
            if _is_not_found(exc):
                target.status = "missing"
                target.detail = "Resource was already missing."
            else:
                target.status = "failed"
                target.detail = str(exc)

    return CleanupPlan(prefix=prefix, apply=True, summary=_build_cleanup_summary(targets, apply=True), targets=targets)


def render_cleanup_plan(plan: CleanupPlan) -> str:
    lines = [
        f"AI Japan Project smoke cleanup ({plan.prefix})",
        f"Apply mode: {'yes' if plan.apply else 'no'}",
        plan.summary,
        "",
    ]
    for target in plan.targets:
        line = f"[{target.status.upper()}] {target.kind}: {target.label}"
        if target.url:
            line += f" ({target.url})"
        if target.detail:
            line += f" - {target.detail}"
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def _local_readiness_checks() -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []
    file_checks = [
        ("Context YAML", CONTEXT_YAML_PATH),
        ("Context Markdown", CONTEXT_MARKDOWN_PATH),
        ("PM Skill", PM_SKILL_PATH),
        ("Critic Skill", CRITIC_SKILL_PATH),
    ]
    for label, path in file_checks:
        exists = path.exists()
        checks.append(
            ReadinessCheck(
                name=label,
                status="pass" if exists else "fail",
                detail=f"{path} {'exists' if exists else 'is missing'}.",
            )
        )
    dir_checks = [
        ("Tasks runtime", TASKS_DIR),
        ("Artifacts runtime", ARTIFACTS_DIR),
        ("Runs runtime", RUNS_DIR),
        ("Smoke receipts", SMOKE_RECEIPTS_DIR),
    ]
    for label, path in dir_checks:
        exists = path.exists()
        checks.append(
            ReadinessCheck(
                name=label,
                status="pass" if exists else "warn",
                detail=f"{path} {'is ready' if exists else 'will be created on demand'}.",
            )
        )
    return checks


def _atlassian_readiness_checks(client: AtlassianServiceClient, settings: AtlassianSettings) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []
    jira_link = join_atlassian_url(client.jira_base_url, "/jira")

    try:
        identity = client.jira_json("GET", "/rest/api/3/myself")
    except Exception as exc:  # noqa: BLE001 - readiness should report failures, not raise them.
        checks.append(
            ReadinessCheck(
                name="Jira identity",
                status="fail",
                detail=_exception_detail(exc),
                link=jira_link,
            )
        )
        checks.append(
            ReadinessCheck(
                name="Atlassian readiness",
                status="warn",
                detail="Live Jira checks stopped early because the initial identity probe failed.",
            )
        )
        return checks

    display_name = identity.get("displayName") or identity.get("publicName") or settings.atlassian_email
    checks.append(
        ReadinessCheck(
            name="Jira identity",
            status="pass",
            detail=f"Authenticated as {display_name}.",
            link=jira_link,
        )
    )

    project_payload: dict | None = None
    try:
        project_payload = client.jira_json("GET", f"/rest/api/3/project/{settings.jira_project_key}")
    except Exception as exc:  # noqa: BLE001 - readiness should keep checking independent systems.
        checks.append(
            ReadinessCheck(
                name="Jira project",
                status="fail",
                detail=_exception_detail(exc),
                link=jira_link,
            )
        )
    else:
        issue_type_names = sorted(
            {
                str(item.get("name") or "").strip()
                for item in project_payload.get("issueTypes") or []
                if str(item.get("name") or "").strip()
            }
        )
        if issue_type_names:
            has_task_type = any(is_task_issue_type_name(name) for name in issue_type_names)
            checks.append(
                ReadinessCheck(
                    name="Jira project",
                    status="pass" if has_task_type else "fail",
                    detail=f"Project {settings.jira_project_key} is reachable. Issue types: {', '.join(issue_type_names)}.",
                    link=jira_link,
                )
            )
        else:
            checks.append(
                ReadinessCheck(
                    name="Jira project",
                    status="warn",
                    detail=f"Project {settings.jira_project_key} is reachable, but issue types were not returned in the project payload.",
                    link=jira_link,
                )
            )

    if project_payload is not None:
        try:
            client.jira_json(
                "POST",
                "/rest/api/3/search/jql",
                {
                    "jql": f'project = "{settings.jira_project_key}" ORDER BY updated DESC',
                    "maxResults": 1,
                    "fields": ["summary"],
                },
            )
        except Exception as exc:  # noqa: BLE001 - readiness should report the endpoint failure.
            checks.append(
                ReadinessCheck(
                    name="Jira search endpoint",
                    status="fail",
                    detail=_exception_detail(exc),
                )
            )
        else:
            checks.append(
                ReadinessCheck(
                    name="Jira search endpoint",
                    status="pass",
                    detail="The project accepts the live /rest/api/3/search/jql endpoint used by the harness.",
                )
            )

        status_check = _build_jira_status_check(client, settings)
        if status_check is not None:
            checks.append(status_check)

    for name, page_id in [
        ("Confluence context parent", settings.confluence_context_parent_id),
        ("Confluence artifacts parent", settings.confluence_artifacts_parent_id),
    ]:
        try:
            payload = client.confluence_json("GET", f"/rest/api/content/{page_id}?expand=body.storage,version")
        except Exception as exc:  # noqa: BLE001 - readiness should report individual parent failures.
            checks.append(
                ReadinessCheck(
                    name=name,
                    status="fail",
                    detail=_exception_detail(exc),
                    link=page_url(client.confluence_base_url, page_id),
                )
            )
        else:
            checks.append(
                ReadinessCheck(
                    name=name,
                    status="pass",
                    detail=f"{payload.get('title', page_id)} is reachable.",
                    link=page_url(client.confluence_base_url, page_id),
                )
            )

    checks.append(
        ReadinessCheck(
            name="Tenant-specific assumptions",
            status="warn",
            detail="The harness assumes live Jira search/jql support, localized workflow aliases when needed, and Confluence content property fallback for metadata.",
        )
    )
    return checks


def _exception_detail(exc: Exception) -> str:
    detail = str(exc).strip()
    if detail:
        return detail
    return exc.__class__.__name__


def _build_jira_status_check(client: AtlassianServiceClient, settings: AtlassianSettings) -> ReadinessCheck | None:
    try:
        payload = client.jira_json("GET", f"/rest/api/3/project/{settings.jira_project_key}/statuses")
    except Exception as exc:  # noqa: BLE001 - readiness should degrade gracefully here.
        return ReadinessCheck(
            name="Jira workflow aliases",
            status="warn",
            detail=f"Could not inspect project workflow statuses: {exc}",
        )

    observed = sorted(_collect_jira_status_names(payload))
    if not observed:
        return ReadinessCheck(
            name="Jira workflow aliases",
            status="warn",
            detail="Project statuses endpoint returned no workflow names.",
        )

    matches = {
        status.value: _matching_statuses(observed, JIRA_STATUS_TARGETS[status].candidate_names)
        for status in JIRA_STATUS_TARGETS
    }
    missing_core = [label for label in (Status.PENDING.value, Status.IN_PROGRESS.value, Status.DONE.value) if not matches[label]]
    missing_optional = [label for label in (Status.REVIEW_REQUESTED.value,) if not matches[label]]
    if missing_core:
        status = "fail"
    elif missing_optional:
        status = "warn"
    else:
        status = "pass"
    details = [f"Observed: {', '.join(observed)}."]
    if missing_core:
        details.append(f"Missing direct aliases for: {', '.join(missing_core)}.")
    if missing_optional:
        details.append(f"No direct alias for: {', '.join(missing_optional)}. Category fallback may still be used.")
    return ReadinessCheck(name="Jira workflow aliases", status=status, detail=" ".join(details))


def _collect_jira_status_names(payload: object) -> set[str]:
    names: set[str] = set()
    if not isinstance(payload, list):
        return names
    for issue_type in payload:
        if not isinstance(issue_type, dict):
            continue
        for status in issue_type.get("statuses") or []:
            if not isinstance(status, dict):
                continue
            name = str(status.get("name") or "").strip()
            if name:
                names.add(name)
    return names


def _matching_statuses(observed: list[str], candidates: tuple[str, ...]) -> list[str]:
    normalized_candidates = {_normalize_status_name(candidate) for candidate in candidates}
    return [name for name in observed if _normalize_status_name(name) in normalized_candidates]


def _normalize_status_name(value: str) -> str:
    return " ".join(value.casefold().split())


def _build_summary(checks: list[ReadinessCheck]) -> str:
    counts = {"pass": 0, "warn": 0, "fail": 0}
    for check in checks:
        counts[check.status] += 1
    return f"{counts['pass']} pass, {counts['warn']} warn, {counts['fail']} fail"


def _overall_status(checks: list[ReadinessCheck]) -> Literal["pass", "warn", "fail"]:
    if any(check.status == "fail" for check in checks):
        return "fail"
    if any(check.status == "warn" for check in checks):
        return "warn"
    return "pass"


def _build_cleanup_targets(receipts: list[SmokeReceipt]) -> list[CleanupTarget]:
    targets: list[CleanupTarget] = []
    seen: set[tuple[str, str]] = set()
    for receipt in receipts:
        issue_key = receipt.jira_issue_key.strip()
        if issue_key and ("jira_issue", issue_key) not in seen:
            targets.append(
                CleanupTarget(
                    kind="jira_issue",
                    identifier=issue_key,
                    label=receipt.task_title,
                    url=receipt.jira_issue_url or None,
                )
            )
            seen.add(("jira_issue", issue_key))

        for label, page_url_value in [
            ("PM artifact", receipt.pm_artifact_url),
            ("Critic review", receipt.critic_review_url),
        ]:
            page_id = _page_id_from_url(page_url_value)
            if page_id and ("confluence_page", page_id) not in seen:
                targets.append(
                    CleanupTarget(
                        kind="confluence_page",
                        identifier=page_id,
                        label=f"{receipt.task_title} - {label}",
                        url=page_url_value,
                    )
                )
                seen.add(("confluence_page", page_id))

        for local_path in [receipt.pm_packet_path, receipt.critic_packet_path]:
            if local_path and ("local_file", local_path) not in seen:
                targets.append(
                    CleanupTarget(
                        kind="local_file",
                        identifier=local_path,
                        label=Path(local_path).name,
                    )
                )
                seen.add(("local_file", local_path))

        if receipt.receipt_path and ("receipt", receipt.receipt_path) not in seen:
            targets.append(
                CleanupTarget(
                    kind="receipt",
                    identifier=receipt.receipt_path,
                    label=Path(receipt.receipt_path).name,
                )
            )
            seen.add(("receipt", receipt.receipt_path))

    return targets


def _build_cleanup_summary(targets: list[CleanupTarget], *, apply: bool) -> str:
    if not targets:
        return "No smoke resources matched the current prefix."
    if not apply:
        return f"{len(targets)} smoke resources are queued for cleanup."
    counts = {"deleted": 0, "missing": 0, "failed": 0, "planned": 0}
    for target in targets:
        counts[target.status] += 1
    return f"{counts['deleted']} deleted, {counts['missing']} already missing, {counts['failed']} failed."


def _page_id_from_url(url: str) -> str | None:
    if not url or "://" not in url:
        return None
    parsed = urlparse(url)
    values = parse_qs(parsed.query).get("pageId") or []
    page_id = values[0] if values else ""
    return page_id if page_id.isdigit() else None


def _resolve_local_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (Path.cwd() / candidate).resolve()


def _is_not_found(exc: Exception) -> bool:
    if hasattr(exc, "status_code") and getattr(exc, "status_code") == 404:
        return True
    return "404" in str(exc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
