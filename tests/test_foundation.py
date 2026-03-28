from __future__ import annotations

from ai_japan_project.atlassian import (
    PAGE_META_PREFIX,
    PAGE_META_SUFFIX,
    build_page_body,
    parse_page_metadata,
    task_status_to_jira,
)
from ai_japan_project.models import Status
from ai_japan_project.settings import AppMode, AppSettings


def test_app_settings_defaults_to_local(monkeypatch) -> None:
    monkeypatch.delenv("AJP_MODE", raising=False)
    settings = AppSettings.from_env()
    assert settings.mode == AppMode.LOCAL


def test_app_settings_reads_atlassian_env(monkeypatch) -> None:
    monkeypatch.setenv("AJP_MODE", "atlassian")
    monkeypatch.setenv("ATLASSIAN_EMAIL", "demo@example.com")
    monkeypatch.setenv("ATLASSIAN_API_TOKEN", "token")
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net/")
    monkeypatch.setenv("JIRA_PROJECT_KEY", "AJP")
    monkeypatch.setenv("CONFLUENCE_BASE_URL", "https://example.atlassian.net/wiki/")
    monkeypatch.setenv("CONFLUENCE_SPACE_KEY", "DEMO")
    monkeypatch.setenv("CONFLUENCE_CONTEXT_PARENT_ID", "100")
    monkeypatch.setenv("CONFLUENCE_ARTIFACTS_PARENT_ID", "200")

    settings = AppSettings.from_env()

    assert settings.mode == AppMode.ATLASSIAN
    assert settings.jira_base_url == "https://example.atlassian.net"
    assert settings.confluence_base_url == "https://example.atlassian.net/wiki"
    settings.validate_atlassian()


def test_task_status_to_jira_mapping() -> None:
    assert task_status_to_jira(Status.PENDING) == "To Do"
    assert task_status_to_jira(Status.IN_PROGRESS) == "In Progress"
    assert task_status_to_jira(Status.REVISION_NEEDED) == "In Progress"
    assert task_status_to_jira(Status.REVIEW_REQUESTED) == "In Review"
    assert task_status_to_jira(Status.DONE) == "Done"


def test_build_page_body_round_trip_metadata() -> None:
    metadata = {"artifact": {"id": "artifact_123", "task_id": "task_123"}}
    body = build_page_body("Demo Page", metadata, "# Heading\n\n- one")

    assert body.startswith(PAGE_META_PREFIX)
    assert PAGE_META_SUFFIX in body
    assert "<h1>Demo Page</h1>" in body
    assert "<h2>Heading</h2>" in body
    assert "<li>one</li>" in body
    assert parse_page_metadata(body) == metadata
