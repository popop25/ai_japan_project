from __future__ import annotations

import io
import json
from urllib import error

import pytest

import ai_japan_project.factory as factory_module
from ai_japan_project.atlassian import (
    PAGE_META_PREFIX,
    PAGE_META_SUFFIX,
    AtlassianClient,
    build_basic_auth_header,
    build_page_body,
    parse_page_metadata,
    task_status_to_jira,
)
from ai_japan_project.models import Status
from ai_japan_project.settings import AppMode, AppSettings


class FakeHTTPResponse:
    def __init__(self, payload: dict | None = None) -> None:
        self.payload = payload or {}

    def __enter__(self) -> "FakeHTTPResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _set_valid_atlassian_env(
    monkeypatch,
    *,
    confluence_base_url: str = "https://example.atlassian.net/wiki/",
    confluence_context_parent_id: str = "100",
    confluence_artifacts_parent_id: str = "200",
) -> None:
    monkeypatch.setenv("AJP_MODE", "atlassian")
    monkeypatch.setenv("ATLASSIAN_EMAIL", " demo@example.com ")
    monkeypatch.setenv("ATLASSIAN_API_TOKEN", " token ")
    monkeypatch.setenv("JIRA_BASE_URL", " https://example.atlassian.net/ ")
    monkeypatch.setenv("JIRA_PROJECT_KEY", "AJP")
    monkeypatch.setenv("CONFLUENCE_BASE_URL", confluence_base_url)
    monkeypatch.setenv("CONFLUENCE_SPACE_KEY", "DEMO")
    monkeypatch.setenv("CONFLUENCE_CONTEXT_PARENT_ID", confluence_context_parent_id)
    monkeypatch.setenv("CONFLUENCE_ARTIFACTS_PARENT_ID", confluence_artifacts_parent_id)


def test_app_settings_defaults_to_local(monkeypatch) -> None:
    monkeypatch.delenv("AJP_MODE", raising=False)
    settings = AppSettings.from_env()
    assert settings.mode == AppMode.LOCAL


def test_app_settings_reads_and_normalizes_atlassian_env(monkeypatch) -> None:
    _set_valid_atlassian_env(monkeypatch)

    settings = AppSettings.from_env()
    resolved = settings.atlassian_settings()

    assert settings.mode == AppMode.ATLASSIAN
    assert resolved.atlassian_email == "demo@example.com"
    assert resolved.atlassian_api_token == "token"
    assert resolved.jira_base_url == "https://example.atlassian.net"
    assert resolved.confluence_base_url == "https://example.atlassian.net/wiki"


def test_app_settings_reports_missing_atlassian_values(monkeypatch) -> None:
    monkeypatch.setenv("AJP_MODE", "atlassian")
    monkeypatch.setenv("ATLASSIAN_EMAIL", "demo@example.com")

    settings = AppSettings.from_env()

    with pytest.raises(ValueError, match="ATLASSIAN_API_TOKEN"):
        settings.validate_atlassian()


def test_app_settings_requires_confluence_wiki_root(monkeypatch) -> None:
    _set_valid_atlassian_env(monkeypatch, confluence_base_url="https://example.atlassian.net/")

    settings = AppSettings.from_env()

    with pytest.raises(ValueError, match=r"CONFLUENCE_BASE_URL must match https://example\.atlassian\.net/wiki"):
        settings.validate_atlassian()


def test_app_settings_requires_numeric_confluence_parent_ids(monkeypatch) -> None:
    _set_valid_atlassian_env(monkeypatch, confluence_context_parent_id="ctx-root")

    settings = AppSettings.from_env()

    with pytest.raises(ValueError, match="CONFLUENCE_CONTEXT_PARENT_ID must be a numeric Confluence page ID"):
        settings.validate_atlassian()


def test_build_project_service_keeps_local_mode_isolated(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_project_service(**kwargs):
        captured.update(kwargs)
        return captured

    monkeypatch.setattr(factory_module, "ProjectService", fake_project_service)
    monkeypatch.setattr(factory_module, "LocalPromptHandoffService", lambda: "prompt")
    monkeypatch.setattr(factory_module, "LocalRunStore", lambda: "run_store")
    monkeypatch.setattr(factory_module, "LocalContextStore", lambda: "local_context")
    monkeypatch.setattr(factory_module, "LocalTaskStore", lambda: "local_task_store")
    monkeypatch.setattr(factory_module, "LocalArtifactStore", lambda: "local_artifact_store")

    settings = AppSettings(
        mode=AppMode.LOCAL,
        confluence_base_url="https://example.atlassian.net",
        confluence_context_parent_id="not-a-page-id",
    )

    service = factory_module.build_project_service(settings)

    assert service["context_store"] == "local_context"
    assert service["task_store"] == "local_task_store"
    assert service["artifact_store"] == "local_artifact_store"
    assert service["run_store"] == "run_store"
    assert service["prompt_service"] == "prompt"


def test_build_project_service_wires_atlassian_mode_without_network(monkeypatch) -> None:
    captured: dict[str, object] = {}
    captured_factory: dict[str, object] = {}

    def fake_project_service(**kwargs):
        captured.update(kwargs)
        return captured

    def fake_client_factory(config):
        captured_factory["config"] = config
        return "client"

    monkeypatch.setattr(factory_module, "ProjectService", fake_project_service)
    monkeypatch.setattr(factory_module, "LocalPromptHandoffService", lambda: "prompt")
    monkeypatch.setattr(factory_module, "LocalRunStore", lambda: "run_store")
    monkeypatch.setattr(factory_module, "LocalContextStore", lambda: "local_context_store")
    monkeypatch.setattr(
        factory_module,
        "AtlassianContextStore",
        lambda client, **kwargs: ("atlassian_context_store", client, kwargs),
    )
    monkeypatch.setattr(
        factory_module,
        "AtlassianTaskStore",
        lambda client, project_key: ("atlassian_task_store", client, project_key),
    )
    monkeypatch.setattr(
        factory_module,
        "AtlassianArtifactStore",
        lambda client, **kwargs: ("atlassian_artifact_store", client, kwargs),
    )

    settings = AppSettings(
        mode=AppMode.ATLASSIAN,
        atlassian_email="demo@example.com",
        atlassian_api_token="token",
        jira_base_url="https://example.atlassian.net",
        jira_project_key="AJP",
        confluence_base_url="https://example.atlassian.net/wiki",
        confluence_space_key="DEMO",
        confluence_context_parent_id="100",
        confluence_artifacts_parent_id="200",
    )

    service = factory_module.build_project_service(
        settings,
        atlassian_client_factory=fake_client_factory,
    )

    config = captured_factory["config"]
    assert config.jira_base_url == "https://example.atlassian.net"
    assert config.confluence_base_url == "https://example.atlassian.net/wiki"
    assert service["context_store"] == (
        "atlassian_context_store",
        "client",
        {
            "space_key": "DEMO",
            "parent_page_id": "100",
            "bootstrap_store": "local_context_store",
        },
    )
    assert service["task_store"] == ("atlassian_task_store", "client", "AJP")
    assert service["artifact_store"] == (
        "atlassian_artifact_store",
        "client",
        {
            "space_key": "DEMO",
            "parent_page_id": "200",
        },
    )
    assert service["run_store"] == "run_store"
    assert service["prompt_service"] == "prompt"


def test_atlassian_client_builds_expected_cloud_urls_and_auth_header() -> None:
    requests: list[tuple[object, int]] = []

    def fake_opener(req, timeout=30):
        requests.append((req, timeout))
        return FakeHTTPResponse({"ok": True})

    client = AtlassianClient(
        email="demo@example.com",
        api_token="token",
        jira_base_url="https://example.atlassian.net",
        confluence_base_url="https://example.atlassian.net/wiki",
        opener=fake_opener,
    )

    client.jira_json("GET", "/rest/api/3/project/AJP")
    client.confluence_json("GET", "/rest/api/content?spaceKey=DEMO")

    jira_request, jira_timeout = requests[0]
    confluence_request, confluence_timeout = requests[1]

    assert jira_request.full_url == "https://example.atlassian.net/rest/api/3/project/AJP"
    assert confluence_request.full_url == "https://example.atlassian.net/wiki/rest/api/content?spaceKey=DEMO"
    assert jira_request.get_header("Authorization") == build_basic_auth_header("demo@example.com", "token")
    assert jira_request.get_method() == "GET"
    assert confluence_request.get_method() == "GET"
    assert jira_timeout == 30
    assert confluence_timeout == 30


def test_atlassian_client_surfaces_http_errors_with_method_and_path() -> None:
    def fake_opener(req, timeout=30):
        raise error.HTTPError(
            url=req.full_url,
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=io.BytesIO(b'{"errorMessages": ["bad auth"]}'),
        )

    client = AtlassianClient(
        email="demo@example.com",
        api_token="token",
        jira_base_url="https://example.atlassian.net",
        confluence_base_url="https://example.atlassian.net/wiki",
        opener=fake_opener,
    )

    with pytest.raises(ValueError, match=r"Atlassian API error 401 for GET /rest/api/3/myself"):
        client.jira_json("GET", "/rest/api/3/myself")


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
