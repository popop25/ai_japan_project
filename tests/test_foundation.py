from __future__ import annotations

import io
import json
from pathlib import Path
from urllib import error

import pytest

import ai_japan_project.factory as factory_module
from ai_japan_project.atlassian import (
    JIRA_LABEL,
    PAGE_META_PREFIX,
    PAGE_META_SUFFIX,
    TASK_PROPERTY_KEY,
    AtlassianApiError,
    AtlassianClient,
    AtlassianTaskStore,
    build_basic_auth_header,
    build_page_body,
    parse_page_metadata,
    task_status_to_jira,
)
from ai_japan_project.models import Status, Task, TaskEvent
from ai_japan_project.settings import AppMode, AppSettings


MISSING_DOTENV_PATH = Path('.tmp_test_runs') / 'missing.env'


class FakeHTTPResponse:
    def __init__(self, payload: dict | None = None) -> None:
        self.payload = payload or {}

    def __enter__(self) -> "FakeHTTPResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class RawHTTPResponse(FakeHTTPResponse):
    def __init__(self, raw: bytes) -> None:
        self.raw = raw

    def read(self) -> bytes:
        return self.raw


class FakeJiraClient:
    jira_base_url = "https://example.atlassian.net"

    def __init__(self, project_key: str = "AJP") -> None:
        self.project_key = project_key
        self._next_issue_number = 1
        self.issues: dict[str, dict] = {}
        self.issue_status_errors: dict[str, Exception] = {}

    def issue(self, issue_key: str) -> dict:
        return self.issues[issue_key]

    def set_issue_status_error(self, issue_key: str, exc: Exception) -> None:
        self.issue_status_errors[issue_key] = exc

    def seed_task_issue(
        self,
        task: Task,
        *,
        issue_key: str | None = None,
        jira_status: str = "To Do",
        status_category: str = "new",
        workflow: dict[str, list[dict]] | None = None,
    ) -> str:
        issue_key = issue_key or self._next_issue_key()
        self.issues[issue_key] = {
            "key": issue_key,
            "fields": {
                "summary": task.title,
                "description": None,
                "labels": [JIRA_LABEL],
            },
            "status_name": jira_status,
            "status_category": status_category,
            "properties": {TASK_PROPERTY_KEY: task.model_dump(mode="json")},
            "comments": [],
            "workflow": workflow or self._default_workflow(),
        }
        return issue_key

    def jira_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        method = method.upper()
        payload = payload or {}

        if (method == "GET" and path.startswith("/rest/api/3/search?")) or (method == "POST" and path == "/rest/api/3/search/jql"):
            return {
                "issues": [
                    {
                        "key": issue["key"],
                        "fields": {
                            "summary": issue["fields"]["summary"],
                            "status": self._status_payload(issue),
                        },
                    }
                    for issue in self.issues.values()
                    if JIRA_LABEL in issue["fields"]["labels"]
                ]
            }

        if method == "POST" and path == "/rest/api/3/issue":
            issue_key = self._next_issue_key()
            fields = payload["fields"]
            self.issues[issue_key] = {
                "key": issue_key,
                "fields": {
                    "summary": fields["summary"],
                    "description": fields.get("description"),
                    "labels": list(fields.get("labels") or []),
                },
                "status_name": "To Do",
                "status_category": "new",
                "properties": {},
                "comments": [],
                "workflow": self._default_workflow(),
            }
            return {"key": issue_key}

        if path.startswith("/rest/api/3/issue/"):
            issue_key, suffix = self._split_issue_path(path)
            if method == "GET" and suffix == "?fields=status" and issue_key in self.issue_status_errors:
                raise self.issue_status_errors[issue_key]
            issue = self.issues.get(issue_key)
            if issue is None:
                raise AtlassianApiError(
                    f"Atlassian API error 404 for {method} {path}: Issue {issue_key} not found",
                    method=method,
                    path=path,
                    status_code=404,
                )

            if method == "PUT" and suffix == "":
                fields = payload["fields"]
                issue["fields"]["summary"] = fields["summary"]
                issue["fields"]["description"] = fields["description"]
                return {}

            if method == "GET" and suffix == "?fields=status":
                return {"fields": {"status": self._status_payload(issue)}}

            if suffix.startswith("/properties/"):
                property_key = suffix.split("/properties/", 1)[1]
                if method == "PUT":
                    issue["properties"][property_key] = payload
                    return {}
                if method == "GET":
                    if property_key not in issue["properties"]:
                        raise AtlassianApiError(
                            f"Atlassian API error 404 for {method} {path}: Property {property_key} not found on {issue_key}",
                            method=method,
                            path=path,
                            status_code=404,
                        )
                    return {"value": issue["properties"][property_key]}

            if suffix == "/transitions":
                if method == "GET":
                    return {"transitions": list(issue["workflow"].get(issue["status_name"], []))}
                if method == "POST":
                    transition_id = payload["transition"]["id"]
                    for transition in issue["workflow"].get(issue["status_name"], []):
                        if transition["id"] != transition_id:
                            continue
                        issue["status_name"] = transition["to"]["name"]
                        issue["status_category"] = transition["to"]["statusCategory"]["key"]
                        return {}
                    raise ValueError(f"Transition not found: {transition_id}")

            if method == "POST" and suffix == "/comment":
                issue["comments"].append(self._extract_adf_text(payload["body"]))
                return {"id": str(len(issue["comments"]))}

        raise AssertionError(f"Unexpected Jira request: {method} {path}")

    def description_text(self, issue_key: str) -> str:
        return self._extract_adf_text(self.issue(issue_key)["fields"]["description"])

    def _next_issue_key(self) -> str:
        issue_key = f"{self.project_key}-{self._next_issue_number}"
        self._next_issue_number += 1
        return issue_key

    def _split_issue_path(self, path: str) -> tuple[str, str]:
        remainder = path[len("/rest/api/3/issue/") :]
        if "/" in remainder:
            issue_key, suffix = remainder.split("/", 1)
            return issue_key, f"/{suffix}"
        if "?" in remainder:
            issue_key, suffix = remainder.split("?", 1)
            return issue_key, f"?{suffix}"
        return remainder, ""

    def _status_payload(self, issue: dict) -> dict:
        return {
            "name": issue["status_name"],
            "statusCategory": {"key": issue["status_category"]},
        }

    def _default_workflow(self) -> dict[str, list[dict]]:
        return {
            "To Do": [self._transition("11", "In Progress", "indeterminate")],
            "Backlog": [self._transition("12", "In Progress", "indeterminate")],
            "Selected for Development": [self._transition("13", "In Progress", "indeterminate")],
            "In Progress": [
                self._transition("21", "In Review", "indeterminate"),
                self._transition("22", "Done", "done"),
            ],
            "Doing": [
                self._transition("31", "In Review", "indeterminate"),
                self._transition("32", "Done", "done"),
            ],
            "Development": [
                self._transition("41", "In Review", "indeterminate"),
                self._transition("42", "Done", "done"),
            ],
            "In Review": [
                self._transition("51", "In Progress", "indeterminate"),
                self._transition("52", "Done", "done"),
            ],
            "Review": [
                self._transition("61", "In Progress", "indeterminate"),
                self._transition("62", "Done", "done"),
            ],
            "Ready for Review": [
                self._transition("71", "Done", "done"),
                self._transition("72", "In Progress", "indeterminate"),
            ],
            "QA Review": [
                self._transition("81", "Done", "done"),
                self._transition("82", "In Progress", "indeterminate"),
            ],
            "Done": [],
            "Closed": [],
            "Resolved": [],
        }

    def _transition(self, transition_id: str, to_name: str, category_key: str) -> dict:
        return {
            "id": transition_id,
            "to": {
                "name": to_name,
                "statusCategory": {"key": category_key},
            },
        }

    def _extract_adf_text(self, document: dict | None) -> str:
        if not document:
            return ""
        lines: list[str] = []
        for block in document.get("content", []):
            text = "".join(node.get("text", "") for node in block.get("content", []))
            if text:
                lines.append(text)
        return "\n".join(lines)


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


def make_task(
    *,
    task_id: str = "task_123",
    title: str = "Requirements Draft Task",
    status: Status = Status.PENDING,
    updated_at: str = "2026-03-29T00:00:00Z",
    refs: dict[str, str] | None = None,
    artifact_ids: list[str] | None = None,
    history: list[TaskEvent] | None = None,
) -> Task:
    return Task(
        id=task_id,
        title=title,
        role="pm",
        deliverable="requirements_draft",
        status=status,
        refs={
            "context": "project/03_context.md",
            "pm_skill": "project/skills/pm.md",
            "critic_skill": "project/skills/critic.md",
            **(refs or {}),
        },
        artifact_ids=artifact_ids or [],
        created_at="2026-03-29T00:00:00Z",
        updated_at=updated_at,
        history=history
        or [
            TaskEvent(
                timestamp="2026-03-29T00:00:00Z",
                event_type="task_created",
                actor="system",
                message="Requirements draft task created.",
                status=status,
            )
        ],
    )


def test_app_settings_defaults_to_local(monkeypatch) -> None:
    monkeypatch.delenv("AJP_MODE", raising=False)
    settings = AppSettings.from_env(dotenv_path=MISSING_DOTENV_PATH)
    assert settings.mode == AppMode.LOCAL


def test_app_settings_reads_and_normalizes_atlassian_env(monkeypatch) -> None:
    _set_valid_atlassian_env(monkeypatch)

    settings = AppSettings.from_env(dotenv_path=MISSING_DOTENV_PATH)
    resolved = settings.atlassian_settings()

    assert settings.mode == AppMode.ATLASSIAN
    assert resolved.atlassian_email == "demo@example.com"
    assert resolved.atlassian_api_token == "token"
    assert resolved.jira_base_url == "https://example.atlassian.net"
    assert resolved.confluence_base_url == "https://example.atlassian.net/wiki"


def test_app_settings_reports_missing_atlassian_values(monkeypatch) -> None:
    monkeypatch.setenv("AJP_MODE", "atlassian")
    monkeypatch.setenv("ATLASSIAN_EMAIL", "demo@example.com")

    settings = AppSettings.from_env(dotenv_path=MISSING_DOTENV_PATH)

    with pytest.raises(ValueError, match="ATLASSIAN_API_TOKEN"):
        settings.validate_atlassian()


def test_app_settings_requires_confluence_wiki_root(monkeypatch) -> None:
    _set_valid_atlassian_env(monkeypatch, confluence_base_url="https://example.atlassian.net/")

    settings = AppSettings.from_env(dotenv_path=MISSING_DOTENV_PATH)

    with pytest.raises(ValueError, match=r"CONFLUENCE_BASE_URL must match https://example\.atlassian\.net/wiki"):
        settings.validate_atlassian()


def test_app_settings_requires_numeric_confluence_parent_ids(monkeypatch) -> None:
    _set_valid_atlassian_env(monkeypatch, confluence_context_parent_id="ctx-root")

    settings = AppSettings.from_env(dotenv_path=MISSING_DOTENV_PATH)

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


def test_atlassian_client_surfaces_invalid_json_payloads() -> None:
    client = AtlassianClient(
        email="demo@example.com",
        api_token="token",
        jira_base_url="https://example.atlassian.net",
        confluence_base_url="https://example.atlassian.net/wiki",
        opener=lambda req, timeout=30: RawHTTPResponse(b"not-json"),
    )

    with pytest.raises(ValueError, match=r"returned invalid JSON"):
        client.jira_json("GET", "/rest/api/3/myself")


def test_task_status_to_jira_mapping() -> None:
    assert task_status_to_jira(Status.PENDING) == "To Do"
    assert task_status_to_jira(Status.IN_PROGRESS) == "In Progress"
    assert task_status_to_jira(Status.REVISION_NEEDED) == "In Progress"
    assert task_status_to_jira(Status.REVIEW_REQUESTED) == "In Review"
    assert task_status_to_jira(Status.DONE) == "Done"


def test_atlassian_task_store_accepts_korean_status_aliases() -> None:
    client = FakeJiraClient(project_key="KAN")
    previous = make_task(task_id="task_korean_alias", status=Status.PENDING)
    issue_key = client.seed_task_issue(previous, jira_status="해야 할 일", status_category="new")
    issue = client.issue(issue_key)
    issue["workflow"] = {
        "해야 할 일": [
            client._transition("101", "진행 중", "indeterminate"),
            client._transition("102", "완료", "done"),
        ],
        "진행 중": [client._transition("201", "완료", "done")],
        "완료": [],
    }
    store = AtlassianTaskStore(client, project_key="KAN")

    updated = previous.model_copy(
        update={
            "status": Status.IN_PROGRESS,
            "updated_at": "2026-03-29T03:00:00Z",
            "history": previous.history
            + [
                TaskEvent(
                    timestamp="2026-03-29T03:00:00Z",
                    event_type="pm_dispatched",
                    actor="system",
                    message="PM packet generated.",
                    status=Status.IN_PROGRESS,
                )
            ],
        }
    )

    saved = store.save(updated)

    assert saved.refs["jira_issue_key"] == issue_key
    assert issue["status_name"] == "진행 중"
    assert issue["comments"][-1] == "PM packet generated."


def test_build_page_body_round_trip_metadata() -> None:
    metadata = {"artifact": {"id": "artifact_123", "task_id": "task_123"}}
    body = build_page_body("Demo Page", metadata, "# Heading\n\n- one")

    assert body.startswith(PAGE_META_PREFIX)
    assert PAGE_META_SUFFIX in body
    assert "<h1>Demo Page</h1>" in body
    assert "<h2>Heading</h2>" in body
    assert "<li>one</li>" in body
    assert parse_page_metadata(body) == metadata


def test_atlassian_task_store_creates_issue_and_saves_property_refs_and_comment() -> None:
    client = FakeJiraClient()
    store = AtlassianTaskStore(client, project_key="AJP")
    task = make_task(artifact_ids=["artifact_001"])

    saved = store.save(task)

    assert saved.refs["jira_issue_key"] == "AJP-1"
    assert saved.refs["jira_issue_url"] == "https://example.atlassian.net/browse/AJP-1"
    issue = client.issue("AJP-1")
    assert issue["properties"][TASK_PROPERTY_KEY]["id"] == task.id
    assert issue["properties"][TASK_PROPERTY_KEY]["artifact_ids"] == ["artifact_001"]
    assert issue["comments"] == ["Requirements draft task created."]
    assert "Task ID: task_123" in client.description_text("AJP-1")
    assert "Artifact IDs: artifact_001" in client.description_text("AJP-1")


def test_atlassian_task_store_reuses_existing_issue_when_task_ref_is_missing() -> None:
    client = FakeJiraClient()
    original = make_task(task_id="task_existing")
    issue_key = client.seed_task_issue(original)
    store = AtlassianTaskStore(client, project_key="AJP")
    updated = original.model_copy(
        update={
            "title": "Updated Requirements Draft",
            "updated_at": "2026-03-29T01:00:00Z",
            "history": original.history
            + [
                TaskEvent(
                    timestamp="2026-03-29T01:00:00Z",
                    event_type="task_updated",
                    actor="system",
                    message="Task title updated.",
                    status=Status.PENDING,
                )
            ],
        }
    )

    saved = store.save(updated)

    assert len(client.issues) == 1
    assert saved.refs["jira_issue_key"] == issue_key
    assert client.issue(issue_key)["fields"]["summary"] == "Updated Requirements Draft"
    assert client.issue(issue_key)["comments"][-1] == "Task title updated."


def test_atlassian_task_store_maps_revision_needed_to_in_progress_with_comment() -> None:
    previous = make_task(task_id="task_revision", status=Status.IN_PROGRESS)
    client = FakeJiraClient()
    issue_key = client.seed_task_issue(previous, jira_status="In Progress", status_category="indeterminate")
    store = AtlassianTaskStore(client, project_key="AJP")
    revised = previous.model_copy(
        update={
            "status": Status.REVISION_NEEDED,
            "updated_at": "2026-03-29T02:00:00Z",
            "history": previous.history
            + [
                TaskEvent(
                    timestamp="2026-03-29T02:00:00Z",
                    event_type="critic_review_ingested",
                    actor="human",
                    message="Revision requested by critic.",
                    status=Status.REVISION_NEEDED,
                )
            ],
        }
    )

    store.save(revised)

    issue = client.issue(issue_key)
    assert issue["status_name"] == "In Progress"
    assert issue["properties"][TASK_PROPERTY_KEY]["status"] == "revision_needed"
    assert "revision_needed" in issue["comments"][-1]
    assert "In Progress" in issue["comments"][-1]


def test_atlassian_task_store_uses_status_category_fallback_for_custom_workflow() -> None:
    previous = make_task(task_id="task_review", status=Status.IN_PROGRESS)
    client = FakeJiraClient()
    workflow = {
        "Development": [client._transition("41", "Done", "done")],
        "Done": [],
    }
    issue_key = client.seed_task_issue(
        previous,
        jira_status="Development",
        status_category="indeterminate",
        workflow=workflow,
    )
    store = AtlassianTaskStore(client, project_key="AJP")
    ready_for_review = previous.model_copy(
        update={
            "status": Status.REVIEW_REQUESTED,
            "updated_at": "2026-03-29T03:00:00Z",
            "history": previous.history
            + [
                TaskEvent(
                    timestamp="2026-03-29T03:00:00Z",
                    event_type="critic_review_ingested",
                    actor="human",
                    message="Review requested.",
                    status=Status.REVIEW_REQUESTED,
                )
            ],
        }
    )

    store.save(ready_for_review)

    issue = client.issue(issue_key)
    assert issue["status_name"] == "Development"
    assert issue["properties"][TASK_PROPERTY_KEY]["status"] == "review_requested"
    assert "Development" in issue["comments"][-1]
    assert "issue property" in issue["comments"][-1]


def test_atlassian_task_store_surfaces_available_transitions_when_sync_fails() -> None:
    previous = make_task(task_id="task_done_blocked")
    client = FakeJiraClient()
    workflow = {
        "To Do": [client._transition("11", "In Progress", "indeterminate")],
        "In Progress": [],
    }
    issue_key = client.seed_task_issue(previous, jira_status="To Do", status_category="new", workflow=workflow)
    store = AtlassianTaskStore(client, project_key="AJP")
    done_task = previous.model_copy(
        update={
            "status": Status.DONE,
            "updated_at": "2026-03-29T04:00:00Z",
            "history": previous.history
            + [
                TaskEvent(
                    timestamp="2026-03-29T04:00:00Z",
                    event_type="task_completed",
                    actor="system",
                    message="Task completed.",
                    status=Status.DONE,
                )
            ],
        }
    )

    with pytest.raises(ValueError, match=r"Available transitions: In Progress"):
        store.save(done_task)

    assert client.issue(issue_key)["properties"][TASK_PROPERTY_KEY]["status"] == "done"


def test_atlassian_task_store_recreates_issue_when_issue_ref_returns_404() -> None:
    client = FakeJiraClient()
    store = AtlassianTaskStore(client, project_key="AJP")
    task = make_task(refs={"jira_issue_key": "AJP-404"})

    saved = store.save(task)

    assert saved.refs["jira_issue_key"] == "AJP-1"
    assert len(client.issues) == 1


def test_atlassian_task_store_refuses_duplicate_creation_when_issue_check_is_unauthorized() -> None:
    client = FakeJiraClient()
    client.set_issue_status_error(
        "AJP-401",
        AtlassianApiError(
            "Atlassian API error 401 for GET /rest/api/3/issue/AJP-401?fields=status: Unauthorized",
            method="GET",
            path="/rest/api/3/issue/AJP-401?fields=status",
            status_code=401,
        ),
    )
    store = AtlassianTaskStore(client, project_key="AJP")
    task = make_task(refs={"jira_issue_key": "AJP-401"})

    with pytest.raises(ValueError, match=r"Refusing to create a new Jira issue.*401"):
        store.save(task)

    assert client.issues == {}


def test_atlassian_task_store_refuses_duplicate_creation_when_issue_check_is_retryable() -> None:
    client = FakeJiraClient()
    client.set_issue_status_error(
        "AJP-429",
        AtlassianApiError(
            "Atlassian API error 429 for GET /rest/api/3/issue/AJP-429?fields=status: Too Many Requests",
            method="GET",
            path="/rest/api/3/issue/AJP-429?fields=status",
            status_code=429,
            retryable=True,
        ),
    )
    store = AtlassianTaskStore(client, project_key="AJP")
    task = make_task(refs={"jira_issue_key": "AJP-429"})

    with pytest.raises(ValueError, match=r"Refusing to create a new Jira issue.*429"):
        store.save(task)

    assert client.issues == {}


def test_atlassian_task_store_refuses_duplicate_creation_when_issue_check_has_network_error() -> None:
    client = FakeJiraClient()
    client.set_issue_status_error(
        "AJP-NET",
        AtlassianApiError(
            "Atlassian API request failed for GET /rest/api/3/issue/AJP-NET?fields=status: timed out",
            method="GET",
            path="/rest/api/3/issue/AJP-NET?fields=status",
            retryable=True,
        ),
    )
    store = AtlassianTaskStore(client, project_key="AJP")
    task = make_task(refs={"jira_issue_key": "AJP-NET"})

    with pytest.raises(ValueError, match=r"Refusing to create a new Jira issue.*timed out"):
        store.save(task)

    assert client.issues == {}


