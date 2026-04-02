from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ai_japan_project.factory import build_project_service
from ai_japan_project.models import Artifact, IngestCriticRequest, IngestPMRequest
from ai_japan_project.operations import CleanupPlan, SmokeReceipt, cleanup_smoke_receipts, load_app_settings, save_smoke_receipt
from ai_japan_project.settings import AppMode
from ai_japan_project.storage import split_frontmatter

DEMO_PREFIX = "[AJP Demo]"
DEMO_TASK_TITLE = "점포 운영 AI 적용 범위 정리"
PM_ARTIFACT_TITLE = "요구사항 정의서 초안"
CRITIC_ARTIFACT_TITLE = "요구사항 초안 검토 의견"

DRAFT_OUTPUT_PATH = REPO_ROOT / "project" / "artifacts" / "demo_requirements_draft.md"
REVIEW_OUTPUT_PATH = REPO_ROOT / "project" / "artifacts" / "demo_requirements_review.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish the current React demo output files to the Atlassian-backed AI Japan Project flow."
    )
    parser.add_argument(
        "--mode",
        choices=[mode.value for mode in AppMode],
        default=AppMode.ATLASSIAN.value,
        help="Runtime mode override. Defaults to atlassian.",
    )
    parser.add_argument("--dotenv", help="Optional path to a .env file.")
    parser.add_argument("--prefix", default=DEMO_PREFIX, help="Receipt prefix used for demo cleanup.")
    parser.add_argument("--title", default=DEMO_TASK_TITLE, help="Title for the Jira task that will be created.")
    parser.add_argument(
        "--cleanup-existing",
        action="store_true",
        help="Delete previous demo resources for the same prefix before publishing.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a text summary.")
    return parser.parse_args()


def read_required_markdown(path: Path) -> str:
    if not path.exists():
        raise ValueError(f"Required demo output file is missing: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Demo output file is empty: {path}")
    if "이 파일은 personal agent가 작성합니다." in text:
        raise ValueError(f"Demo output file still contains the placeholder text: {path}")
    return text + "\n"


def normalize_review_markdown(review_markdown: str) -> str:
    frontmatter, notes = split_frontmatter(review_markdown)
    if not frontmatter:
        raise ValueError("Critic output must include YAML front matter.")

    verdict = str(frontmatter.get("verdict") or "").strip()
    if verdict == "ready_for_decision":
        verdict = "approve"
    if verdict not in {"approve", "revise"}:
        raise ValueError("Critic verdict must be one of approve, ready_for_decision, or revise.")

    def normalize_list(values: object) -> list[str]:
        normalized: list[str] = []
        for value in list(values or []):
            if isinstance(value, dict):
                parts = [f"{key}: {item}" for key, item in value.items()]
                text = ", ".join(parts).strip()
            elif isinstance(value, list):
                text = ", ".join(str(item).strip() for item in value if str(item).strip())
            else:
                text = str(value).strip()
            text = text.replace(":", " - ")
            if text:
                normalized.append(text)
        return normalized

    normalized_frontmatter = {
        "verdict": verdict,
        "summary": str(frontmatter.get("summary") or "").strip(),
        "missing_items": normalize_list(frontmatter.get("missing_items")),
        "recommended_changes": normalize_list(frontmatter.get("recommended_changes")),
    }

    header = yaml.safe_dump(normalized_frontmatter, allow_unicode=True, sort_keys=False).strip()
    body = notes.strip()
    if body:
        return f"---\n{header}\n---\n{body}\n"
    return f"---\n{header}\n---\n"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def latest_artifact(detail, kind: str) -> Artifact:
    matches = [artifact for artifact in detail.artifacts if artifact.kind == kind]
    if not matches:
        raise ValueError(f"No {kind} artifact was created for task {detail.task.id}.")
    matches.sort(key=lambda artifact: artifact.created_at, reverse=True)
    return matches[0]


def maybe_cleanup_existing(settings, *, prefix: str, apply: bool) -> CleanupPlan | None:
    if not apply:
        return None
    return cleanup_smoke_receipts(settings, prefix=prefix, apply=True)


def publish_demo_outputs(*, mode: AppMode, dotenv_path: Path | None, prefix: str, title: str, cleanup_existing: bool) -> tuple[SmokeReceipt, CleanupPlan | None]:
    settings = load_app_settings(mode=mode, dotenv_path=dotenv_path)
    cleanup_plan = maybe_cleanup_existing(settings, prefix=prefix, apply=cleanup_existing)

    draft_markdown = read_required_markdown(DRAFT_OUTPUT_PATH)
    review_markdown = normalize_review_markdown(read_required_markdown(REVIEW_OUTPUT_PATH))

    service = build_project_service(settings)
    context, _ = service.get_context()
    service.save_context(context)

    detail = service.create_requirements_task(title)
    detail = service.dispatch_pm(detail.task.id)
    if detail.pm_packet is None:
        raise ValueError("PM packet was not created while publishing demo outputs.")

    detail = service.ingest_pm(detail.task.id, IngestPMRequest(content=draft_markdown, title=PM_ARTIFACT_TITLE))
    detail = service.dispatch_critic(detail.task.id)
    if detail.critic_packet is None:
        raise ValueError("Critic packet was not created while publishing demo outputs.")

    detail = service.ingest_critic(detail.task.id, IngestCriticRequest(review_markdown=review_markdown))

    critic_artifact = latest_artifact(detail, "critic_review")
    if critic_artifact.title != CRITIC_ARTIFACT_TITLE:
        service.artifact_store.save(critic_artifact.model_copy(update={"title": CRITIC_ARTIFACT_TITLE}))
        detail = service.get_task_detail(detail.task.id)

    pm_artifact = latest_artifact(detail, "pm_output")
    critic_artifact = latest_artifact(detail, "critic_review")

    receipt = SmokeReceipt(
        prefix=prefix,
        created_at=utc_now(),
        task_id=detail.task.id,
        task_title=detail.task.title,
        jira_issue_key=detail.task.refs.get("jira_issue_key", ""),
        jira_issue_url=detail.task.refs.get("jira_issue_url", ""),
        pm_packet_path=str(Path(detail.pm_packet.path).resolve()),
        critic_packet_path=str(Path(detail.critic_packet.path).resolve()),
        pm_artifact_url=pm_artifact.path,
        critic_review_url=critic_artifact.path,
        final_status=detail.task.status.value,
    )
    receipt_path = save_smoke_receipt(receipt)
    return receipt.model_copy(update={"receipt_path": str(receipt_path)}), cleanup_plan


def render_summary(receipt: SmokeReceipt, cleanup_plan: CleanupPlan | None) -> str:
    lines = ["AI Japan Project demo publish completed"]
    if cleanup_plan is not None:
        lines.append(f"- Cleanup: {cleanup_plan.summary}")
    lines.extend(
        [
            f"- Jira issue: {receipt.jira_issue_key} ({receipt.jira_issue_url})",
            f"- PM artifact: {receipt.pm_artifact_url}",
            f"- Critic review: {receipt.critic_review_url}",
            f"- Final status: {receipt.final_status}",
            f"- Receipt: {receipt.receipt_path}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    dotenv_path = Path(args.dotenv).resolve() if args.dotenv else None
    receipt, cleanup_plan = publish_demo_outputs(
        mode=AppMode(args.mode),
        dotenv_path=dotenv_path,
        prefix=args.prefix,
        title=args.title,
        cleanup_existing=args.cleanup_existing,
    )
    if args.json:
        print(
            json.dumps(
                {
                    "cleanup": cleanup_plan.model_dump(mode="json") if cleanup_plan is not None else None,
                    "receipt": receipt.model_dump(mode="json"),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(render_summary(receipt, cleanup_plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
