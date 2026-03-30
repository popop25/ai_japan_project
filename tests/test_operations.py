from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from ai_japan_project.operations import (
    SmokeReceipt,
    build_readiness_report,
    cleanup_smoke_receipts,
    load_smoke_receipts,
    save_smoke_receipt,
)
from ai_japan_project.settings import AppMode, AppSettings


TMP_ROOT = Path('.tmp_test_runs') / 'operations_tests'


class FakeOperationsClient:
    jira_base_url = "https://example.atlassian.net"
    confluence_base_url = "https://example.atlassian.net/wiki"

    def __init__(self) -> None:
        self.deleted_issue_keys: list[str] = []
        self.deleted_page_ids: list[str] = []

    def jira_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        if method == "GET" and path == "/rest/api/3/myself":
            return {"displayName": "Demo User"}
        if method == "GET" and path == "/rest/api/3/project/KAN":
            return {"key": "KAN", "issueTypes": [{"name": "Task"}, {"name": "Bug"}]}
        if method == "POST" and path == "/rest/api/3/search/jql":
            return {"issues": []}
        if method == "GET" and path == "/rest/api/3/project/KAN/statuses":
            return [
                {
                    "name": "Task",
                    "statuses": [
                        {"name": "To Do"},
                        {"name": "In Progress"},
                        {"name": "In Review"},
                        {"name": "Done"},
                    ],
                },
            ]
        if method == "DELETE" and path.startswith("/rest/api/3/issue/"):
            issue_key = path.split("/rest/api/3/issue/", 1)[1].split("?", 1)[0]
            self.deleted_issue_keys.append(issue_key)
            return {}
        raise AssertionError(f"Unexpected Jira request: {method} {path}")

    def confluence_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        if method == "GET" and path.startswith("/rest/api/content/98309"):
            return {
                "id": "98309",
                "title": "Context Parent",
                "body": {"storage": {"value": "<h1>Context</h1>"}},
                "version": {"number": 1},
            }
        if method == "GET" and path.startswith("/rest/api/content/294933"):
            return {
                "id": "294933",
                "title": "Artifacts Parent",
                "body": {"storage": {"value": "<h1>Artifacts</h1>"}},
                "version": {"number": 1},
            }
        if method == "DELETE" and path.startswith("/rest/api/content/"):
            page_id = path.split("/rest/api/content/", 1)[1]
            self.deleted_page_ids.append(page_id)
            return {}
        raise AssertionError(f"Unexpected Confluence request: {method} {path}")


def make_settings() -> AppSettings:
    return AppSettings(
        mode=AppMode.ATLASSIAN,
        atlassian_email="demo@example.com",
        atlassian_api_token="token",
        jira_base_url="https://example.atlassian.net",
        jira_project_key="KAN",
        confluence_base_url="https://example.atlassian.net/wiki",
        confluence_space_key="DEMO",
        confluence_context_parent_id="98309",
        confluence_artifacts_parent_id="294933",
    )


def make_test_root() -> Path:
    root = TMP_ROOT / uuid.uuid4().hex
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_local_readiness_can_be_pointed_at_temp_files(monkeypatch) -> None:
    root = make_test_root()
    try:
        context_yaml = root / "context.yaml"
        context_md = root / "03_context.md"
        pm_skill = root / "pm.md"
        critic_skill = root / "critic.md"
        tasks_dir = root / "tasks"
        artifacts_dir = root / "artifacts"
        runs_dir = root / "runs"
        smoke_dir = runs_dir / "smoke_receipts"

        for path in [context_yaml, context_md, pm_skill, critic_skill]:
            path.write_text("ok\n", encoding="utf-8")
        for path in [tasks_dir, artifacts_dir, runs_dir, smoke_dir]:
            path.mkdir(parents=True, exist_ok=True)

        import ai_japan_project.operations as operations_module

        monkeypatch.setattr(operations_module, "CONTEXT_YAML_PATH", context_yaml)
        monkeypatch.setattr(operations_module, "CONTEXT_MARKDOWN_PATH", context_md)
        monkeypatch.setattr(operations_module, "PM_SKILL_PATH", pm_skill)
        monkeypatch.setattr(operations_module, "CRITIC_SKILL_PATH", critic_skill)
        monkeypatch.setattr(operations_module, "TASKS_DIR", tasks_dir)
        monkeypatch.setattr(operations_module, "ARTIFACTS_DIR", artifacts_dir)
        monkeypatch.setattr(operations_module, "RUNS_DIR", runs_dir)
        monkeypatch.setattr(operations_module, "SMOKE_RECEIPTS_DIR", smoke_dir)

        report = build_readiness_report(AppSettings(mode=AppMode.LOCAL))

        assert report.mode == AppMode.LOCAL
        assert report.overall_status == "pass"
        assert any(check.name == "Context YAML" for check in report.checks)
        assert any(check.name == "Smoke receipts" for check in report.checks)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_atlassian_readiness_reports_connected_tenant_contract() -> None:
    client = FakeOperationsClient()

    report = build_readiness_report(make_settings(), client_factory=lambda _: client)

    assert report.mode == AppMode.ATLASSIAN
    assert report.overall_status == "warn"
    assert any(check.name == "Jira identity" and check.status == "pass" for check in report.checks)
    assert any(check.name == "Jira workflow aliases" and "Observed:" in check.detail for check in report.checks)
    assert any(check.name == "Tenant-specific assumptions" and check.status == "warn" for check in report.checks)


def test_smoke_receipts_round_trip_and_cleanup_apply() -> None:
    root = make_test_root()
    try:
        receipts_dir = root / "receipts"
        pm_packet = root / "pm_packet.md"
        critic_packet = root / "critic_packet.md"
        pm_packet.write_text("pm packet\n", encoding="utf-8")
        critic_packet.write_text("critic packet\n", encoding="utf-8")

        receipt = SmokeReceipt(
            prefix="[AJP Smoke]",
            created_at="2026-03-30T00:00:00Z",
            task_id="task_smoke_001",
            task_title="[AJP Smoke] Requirements Draft",
            jira_issue_key="KAN-10",
            jira_issue_url="https://example.atlassian.net/browse/KAN-10",
            pm_packet_path=str(pm_packet),
            critic_packet_path=str(critic_packet),
            pm_artifact_url="https://example.atlassian.net/wiki/pages/viewpage.action?pageId=12345",
            critic_review_url="https://example.atlassian.net/wiki/pages/viewpage.action?pageId=67890",
            final_status="review_requested",
        )
        receipt_path = save_smoke_receipt(receipt, receipts_dir=receipts_dir)

        loaded = load_smoke_receipts(receipts_dir=receipts_dir)
        assert len(loaded) == 1
        assert loaded[0].receipt_path == str(receipt_path)

        dry_run = cleanup_smoke_receipts(prefix="[AJP Smoke]", receipts_dir=receipts_dir, apply=False)
        assert dry_run.apply is False
        assert len(dry_run.targets) == 6

        client = FakeOperationsClient()
        applied = cleanup_smoke_receipts(
            make_settings(),
            prefix="[AJP Smoke]",
            receipts_dir=receipts_dir,
            apply=True,
            client_factory=lambda _: client,
        )

        assert all(target.status == "deleted" for target in applied.targets)
        assert client.deleted_issue_keys == ["KAN-10"]
        assert client.deleted_page_ids == ["12345", "67890"]
        assert not pm_packet.exists()
        assert not critic_packet.exists()
        assert not receipt_path.exists()
    finally:
        shutil.rmtree(root, ignore_errors=True)
