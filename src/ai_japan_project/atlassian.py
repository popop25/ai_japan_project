from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from html import escape, unescape
from typing import TYPE_CHECKING, Callable, Protocol
from urllib import error, parse, request

from pydantic import ValidationError

from .interfaces import ArtifactStore, ContextStore, TaskStore
from .models import Artifact, ProjectContext, Status, Task
from .renderers import render_artifact_page_markdown, render_context_markdown
from .storage import LocalContextStore

if TYPE_CHECKING:
    from .settings import AtlassianSettings

TASK_PROPERTY_KEY = "ai_japan_project.task"
PAGE_META_PREFIX = "<!-- AJP_META:"
PAGE_META_SUFFIX = "-->"
JIRA_LABEL = "ai-japan-project"
CONFLUENCE_PAGE_BATCH_SIZE = 100
PAGE_META_SCHEMA_VERSION = 1
CONFLUENCE_META_PROPERTY_KEY = "ai_japan_project.meta"


class AtlassianResponse(Protocol):
    def __enter__(self) -> "AtlassianResponse": ...
    def __exit__(self, exc_type, exc, tb) -> None: ...
    def read(self) -> bytes: ...


class AtlassianApiError(ValueError):
    def __init__(
        self,
        message: str,
        *,
        method: str,
        path: str,
        status_code: int | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.method = method
        self.path = path
        self.status_code = status_code
        self.retryable = retryable


class JiraApiClient(Protocol):
    jira_base_url: str

    def jira_json(self, method: str, path: str, payload: dict | None = None) -> dict: ...


class ConfluenceApiClient(Protocol):
    confluence_base_url: str

    def confluence_json(self, method: str, path: str, payload: dict | None = None) -> dict: ...


class AtlassianServiceClient(JiraApiClient, ConfluenceApiClient, Protocol):
    pass


UrlOpenFn = Callable[..., AtlassianResponse]


@dataclass(frozen=True)
class JiraStatusTarget:
    primary_name: str
    category_key: str
    fallback_names: tuple[str, ...] = ()

    @property
    def candidate_names(self) -> tuple[str, ...]:
        return (self.primary_name, *self.fallback_names)


@dataclass(frozen=True)
class JiraStatusSyncResult:
    jira_status_name: str
    note: str | None = None


JIRA_STATUS_TARGETS: dict[Status, JiraStatusTarget] = {
    Status.PENDING: JiraStatusTarget("To Do", "new", ("Backlog", "Selected for Development", "해야 할 일")),
    Status.IN_PROGRESS: JiraStatusTarget("In Progress", "indeterminate", ("Doing", "Development", "진행 중")),
    Status.REVISION_NEEDED: JiraStatusTarget("In Progress", "indeterminate", ("Doing", "Development", "진행 중")),
    Status.REVIEW_REQUESTED: JiraStatusTarget("In Review", "indeterminate", ("Review", "Ready for Review", "QA Review", "검토 중", "리뷰 중")),
    Status.DONE: JiraStatusTarget("Done", "done", ("Closed", "Resolved", "완료")),
}


def build_basic_auth_header(email: str, api_token: str) -> str:
    auth_pair = f"{email}:{api_token}".encode("utf-8")
    return "Basic " + base64.b64encode(auth_pair).decode("ascii")


def join_atlassian_url(base_url: str, path: str) -> str:
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url.rstrip('/')}" + normalized_path


class AtlassianClient:
    @classmethod
    def from_settings(
        cls,
        settings: "AtlassianSettings",
        opener: UrlOpenFn | None = None,
    ) -> "AtlassianClient":
        return cls(
            email=settings.atlassian_email,
            api_token=settings.atlassian_api_token,
            jira_base_url=settings.jira_base_url,
            confluence_base_url=settings.confluence_base_url,
            opener=opener,
        )

    def __init__(
        self,
        *,
        email: str,
        api_token: str,
        jira_base_url: str,
        confluence_base_url: str,
        opener: UrlOpenFn | None = None,
    ) -> None:
        self.auth_header = build_basic_auth_header(email, api_token)
        self.jira_base_url = jira_base_url.rstrip("/")
        self.confluence_base_url = confluence_base_url.rstrip("/")
        self._opener = opener or request.urlopen

    def jira_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        return self._json_request(self.jira_base_url, method, path, payload)

    def confluence_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        return self._json_request(self.confluence_base_url, method, path, payload)

    def _json_request(self, base_url: str, method: str, path: str, payload: dict | None = None) -> dict:
        normalized_method = method.upper()
        url = join_atlassian_url(base_url, path)
        data = None
        headers = {
            "Authorization": self.auth_header,
            "Accept": "application/json",
        }
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = request.Request(url, data=data, headers=headers, method=normalized_method)
        try:
            with self._opener(req, timeout=30) as response:
                text = response.read().decode("utf-8")
                if not text:
                    return {}
                try:
                    return json.loads(text)
                except json.JSONDecodeError as exc:
                    raise AtlassianApiError(
                        f"Atlassian API returned invalid JSON for {normalized_method} {path}: {text[:200]}",
                        method=normalized_method,
                        path=path,
                    ) from exc
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise AtlassianApiError(
                f"Atlassian API error {exc.code} for {normalized_method} {path}: {body}",
                method=normalized_method,
                path=path,
                status_code=exc.code,
                retryable=exc.code in {429, 500, 502, 503, 504},
            ) from exc
        except error.URLError as exc:
            raise AtlassianApiError(
                f"Atlassian API request failed for {normalized_method} {path}: {exc.reason}",
                method=normalized_method,
                path=path,
                retryable=True,
            ) from exc


def jira_status_target(status: Status) -> JiraStatusTarget:
    return JIRA_STATUS_TARGETS[status]


def task_status_to_jira(status: Status) -> str:
    return jira_status_target(status).primary_name


def render_issue_description(task: Task) -> dict:
    lines = [
        "AI Japan Project Task",
        f"Task ID: {task.id}",
        f"Role: {task.role}",
        f"Deliverable: {task.deliverable}",
        f"Internal Status: {task.status.value}",
    ]
    if task.latest_run_id:
        lines.append(f"Latest Run ID: {task.latest_run_id}")
    if task.artifact_ids:
        lines.append(f"Artifact IDs: {', '.join(task.artifact_ids)}")
    for key, value in sorted(task.refs.items()):
        if key in {"jira_issue_key", "jira_issue_url"}:
            continue
        lines.append(f"Ref {key}: {value}")
    return _adf_doc("\n".join(lines))


def _adf_doc(text: str) -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text}],
            }
        ],
    }


def build_page_body(title: str, metadata: dict, markdown_body: str) -> str:
    meta_json = escape(json.dumps(metadata, ensure_ascii=False))
    rendered_body = markdown_to_storage(markdown_body)
    return f"{PAGE_META_PREFIX}{meta_json}{PAGE_META_SUFFIX}<h1>{escape(title)}</h1>{rendered_body}"


def parse_page_metadata(storage_value: str) -> dict:
    start = storage_value.find(PAGE_META_PREFIX)
    if start == -1:
        return {}
    end = storage_value.find(PAGE_META_SUFFIX, start)
    if end == -1:
        return {}
    raw_json = storage_value[start + len(PAGE_META_PREFIX) : end]
    try:
        payload = json.loads(unescape(raw_json))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def markdown_to_storage(markdown: str) -> str:
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    list_tag: str | None = None
    code_lines: list[str] = []
    in_code_block = False

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        blocks.append(f"<p>{escape(' '.join(paragraph_lines))}</p>")
        paragraph_lines.clear()

    def flush_list() -> None:
        nonlocal list_tag
        if not list_tag:
            return
        blocks.append(f"<{list_tag}>")
        blocks.extend(list_items)
        blocks.append(f"</{list_tag}>")
        list_items.clear()
        list_tag = None

    def flush_code_block() -> None:
        nonlocal in_code_block
        if not code_lines:
            in_code_block = False
            return
        code_text = "\n".join(code_lines)
        blocks.append(f"<pre><code>{escape(code_text)}</code></pre>")
        code_lines.clear()
        in_code_block = False

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if in_code_block:
            if stripped.startswith("```"):
                flush_code_block()
            else:
                code_lines.append(raw_line)
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            in_code_block = True
            code_lines.clear()
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        if stripped == "---":
            flush_paragraph()
            flush_list()
            blocks.append("<hr />")
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h2>{escape(stripped[2:])}</h2>")
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h3>{escape(stripped[3:])}</h3>")
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            flush_list()
            blocks.append(f"<h4>{escape(stripped[4:])}</h4>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            if list_tag not in {None, "ul"}:
                flush_list()
            list_tag = "ul"
            list_items.append(f"<li>{escape(stripped[2:])}</li>")
            continue

        ordered_marker, separator, ordered_value = stripped.partition(". ")
        if separator and ordered_marker.isdigit():
            flush_paragraph()
            if list_tag not in {None, "ol"}:
                flush_list()
            list_tag = "ol"
            list_items.append(f"<li>{escape(ordered_value)}</li>")
            continue

        flush_list()
        paragraph_lines.append(stripped)

    flush_paragraph()
    flush_list()
    flush_code_block()
    return "".join(blocks)


def page_url(base_url: str, page_id: str) -> str:
    return join_atlassian_url(base_url, f"/pages/viewpage.action?pageId={page_id}")


def update_task_ref(task: Task, **refs: str) -> Task:
    merged = {**task.refs, **refs}
    return task.model_copy(update={"refs": merged})


class AtlassianTaskStore(TaskStore):
    def __init__(self, client: JiraApiClient, project_key: str) -> None:
        self.client = client
        self.project_key = project_key

    def list(self) -> list[Task]:
        tasks: list[Task] = []
        for issue in self._search_issues():
            task = self._load_task_from_issue(issue)
            if task is not None:
                tasks.append(task)
        return tasks

    def get(self, task_id: str) -> Task | None:
        for issue in self._search_issues():
            task = self._load_task_from_issue(issue)
            if task is None:
                continue
            if task.id == task_id or task.refs.get("jira_issue_key") == task_id:
                return task
        return None

    def save(self, task: Task) -> Task:
        previous_task = self._load_previous_task(task)
        issue_key = self._resolve_issue_key(task, previous_task)
        try:
            existing_issue = issue_key is not None
            if issue_key is None:
                issue_key = self._create_issue(task)
            task = self._sync_remote_refs(task, issue_key)
            if existing_issue:
                self._update_issue(issue_key, task)
            self._save_property(issue_key, task)
            status_result = self._sync_status(issue_key, task.status)
            comment = self._build_comment(task, previous_task, status_result)
            if comment is not None:
                self._add_comment(issue_key, comment)
            return task
        except ValueError as exc:
            issue_label = issue_key or task.refs.get("jira_issue_key") or "[new issue]"
            raise ValueError(f"Failed to sync Jira issue {issue_label} for task {task.id}: {exc}") from exc

    def _search_issues(self) -> list[dict]:
        payload = {
            "jql": f'project = "{self.project_key}" AND labels = "{JIRA_LABEL}" ORDER BY updated DESC',
            "maxResults": 100,
            "fields": ["summary", "status"],
        }
        return self.client.jira_json("POST", "/rest/api/3/search/jql", payload).get("issues", [])

    def _create_issue(self, task: Task) -> str:
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": task.title,
                "issuetype": {"name": "Task"},
                "labels": [JIRA_LABEL],
                "description": render_issue_description(task),
            }
        }
        response = self.client.jira_json("POST", "/rest/api/3/issue", payload)
        return response["key"]

    def _update_issue(self, issue_key: str, task: Task) -> None:
        payload = {"fields": {"summary": task.title, "description": render_issue_description(task)}}
        self.client.jira_json("PUT", f"/rest/api/3/issue/{issue_key}", payload)

    def _save_property(self, issue_key: str, task: Task) -> None:
        self.client.jira_json(
            "PUT",
            f"/rest/api/3/issue/{issue_key}/properties/{TASK_PROPERTY_KEY}",
            task.model_dump(mode="json"),
        )

    def _load_task_from_issue(self, issue: dict) -> Task | None:
        issue_key = issue["key"]
        try:
            payload = self.client.jira_json("GET", f"/rest/api/3/issue/{issue_key}/properties/{TASK_PROPERTY_KEY}")
            task = Task.model_validate(payload.get("value") or {})
        except ValidationError:
            return None
        except ValueError as exc:
            if _is_not_found_error(exc):
                return None
            raise
        return self._sync_remote_refs(task, issue_key)

    def _load_previous_task(self, task: Task) -> Task | None:
        issue_key = task.refs.get("jira_issue_key")
        if issue_key:
            previous = self._load_task_by_issue_key(issue_key)
            if previous is not None:
                return previous
        return self.get(task.id)

    def _load_task_by_issue_key(self, issue_key: str) -> Task | None:
        try:
            payload = self.client.jira_json("GET", f"/rest/api/3/issue/{issue_key}/properties/{TASK_PROPERTY_KEY}")
            task = Task.model_validate(payload.get("value") or {})
        except ValidationError:
            return None
        except ValueError as exc:
            if _is_not_found_error(exc):
                return None
            raise
        return self._sync_remote_refs(task, issue_key)

    def _resolve_issue_key(self, task: Task, previous_task: Task | None) -> str | None:
        if previous_task is not None:
            return previous_task.refs.get("jira_issue_key") or task.refs.get("jira_issue_key")
        issue_key = task.refs.get("jira_issue_key")
        if not issue_key:
            return None
        try:
            if self._issue_exists(issue_key):
                return issue_key
        except ValueError as exc:
            raise ValueError(
                f"Could not verify whether Jira issue {issue_key} still exists. Refusing to create a new Jira issue for task {task.id} until this check succeeds: {exc}"
            ) from exc
        return None

    def _issue_exists(self, issue_key: str) -> bool:
        try:
            self._issue_status(issue_key)
        except ValueError as exc:
            if _is_not_found_error(exc):
                return False
            raise
        return True

    def _sync_remote_refs(self, task: Task, issue_key: str) -> Task:
        return update_task_ref(
            task,
            jira_issue_key=issue_key,
            jira_issue_url=join_atlassian_url(self.client.jira_base_url, f"/browse/{issue_key}"),
        )

    def _sync_status(self, issue_key: str, status: Status) -> JiraStatusSyncResult:
        target = jira_status_target(status)
        current_name, current_category = self._issue_status(issue_key)
        if _matches_status(current_name, target.candidate_names):
            return JiraStatusSyncResult(
                jira_status_name=current_name,
                note=_status_sync_note(status, current_name),
            )
        transitions = self.client.jira_json("GET", f"/rest/api/3/issue/{issue_key}/transitions")
        available_transitions = transitions.get("transitions", [])
        for transition in available_transitions:
            to_status = transition.get("to", {})
            to_name = to_status.get("name", "")
            if not _matches_status(to_name, target.candidate_names):
                continue
            transition_id = transition.get("id")
            if not transition_id:
                continue
            try:
                self.client.jira_json(
                    "POST",
                    f"/rest/api/3/issue/{issue_key}/transitions",
                    {"transition": {"id": transition_id}},
                )
            except ValueError as exc:
                refreshed_name, _ = self._issue_status(issue_key)
                if _matches_status(refreshed_name, target.candidate_names):
                    return JiraStatusSyncResult(
                        jira_status_name=refreshed_name,
                        note=_status_sync_note(status, refreshed_name),
                    )
                raise ValueError(
                    self._build_transition_error(
                        issue_key=issue_key,
                        status=status,
                        current_name=current_name,
                        available_transitions=available_transitions,
                        cause=str(exc),
                    )
                ) from exc
            return JiraStatusSyncResult(
                jira_status_name=to_name or target.primary_name,
                note=_status_sync_note(status, to_name or target.primary_name),
            )
        if current_category == target.category_key:
            return JiraStatusSyncResult(
                jira_status_name=current_name,
                note=_category_fallback_note(status, current_name, target.primary_name),
            )
        raise ValueError(
            self._build_transition_error(
                issue_key=issue_key,
                status=status,
                current_name=current_name,
                available_transitions=available_transitions,
            )
        )

    def _build_transition_error(
        self,
        *,
        issue_key: str,
        status: Status,
        current_name: str,
        available_transitions: list[dict],
        cause: str | None = None,
    ) -> str:
        target = jira_status_target(status).primary_name
        available = ", ".join(_transition_names(available_transitions)) or "(none)"
        message = (
            f"Unable to move Jira issue {issue_key} from '{current_name}' to '{target}' "
            f"for internal status '{status.value}'. Available transitions: {available}."
        )
        if cause:
            return f"{message} Last transition error: {cause}"
        return message

    def _issue_status(self, issue_key: str) -> tuple[str, str | None]:
        issue = self.client.jira_json("GET", f"/rest/api/3/issue/{issue_key}?fields=status")
        status = issue["fields"]["status"]
        return status["name"], status.get("statusCategory", {}).get("key")

    def _build_comment(
        self,
        task: Task,
        previous_task: Task | None,
        status_result: JiraStatusSyncResult,
    ) -> str | None:
        notes: list[str] = []
        if status_result.note:
            notes.append(status_result.note)
        if previous_task is not None and previous_task.status == Status.REVISION_NEEDED and task.status == Status.IN_PROGRESS:
            notes.append("Revision work has resumed.")
        latest_changed = previous_task is None or _latest_event_key(previous_task) != _latest_event_key(task)
        if latest_changed:
            base_message = task.history[-1].message if task.history else f"Task updated: {task.title}"
        elif previous_task is not None and previous_task.status != task.status and notes:
            base_message = f"Task status synced to {task.status.value}."
        else:
            return None
        if not notes:
            return base_message
        return base_message + "\n\n" + _dedupe_notes(notes)

    def _add_comment(self, issue_key: str, message: str) -> None:
        self.client.jira_json(
            "POST",
            f"/rest/api/3/issue/{issue_key}/comment",
            {"body": _adf_doc(message)},
        )


class AtlassianContextStore(ContextStore):
    CONTEXT_TITLE = "03_Context"

    def __init__(
        self,
        client: ConfluenceApiClient,
        *,
        space_key: str,
        parent_page_id: str,
        bootstrap_store: LocalContextStore | None = None,
    ) -> None:
        self.client = client
        self.space_key = space_key
        self.parent_page_id = parent_page_id
        self.bootstrap_store = bootstrap_store

    def load(self) -> ProjectContext:
        page = self._find_page(self.CONTEXT_TITLE)
        if page is None:
            return self._bootstrap_context_page()
        metadata = _page_metadata(self.client, page)
        context_payload = metadata.get("context")
        if not context_payload:
            return self._bootstrap_context_page()
        try:
            return ProjectContext.model_validate(context_payload)
        except ValidationError as exc:
            raise ValueError("Confluence context page contains invalid canonical context metadata.") from exc

    def load_markdown(self) -> str:
        page = self._find_page(self.CONTEXT_TITLE)
        if page is None:
            return self._bootstrap_context_markdown()
        metadata = _page_metadata(self.client, page)
        stored_markdown = metadata.get("markdown")
        if isinstance(stored_markdown, str) and stored_markdown.strip():
            return stored_markdown if stored_markdown.endswith("\n") else stored_markdown + "\n"
        context_payload = metadata.get("context")
        if context_payload:
            return render_context_markdown(ProjectContext.model_validate(context_payload))
        return self._bootstrap_context_markdown()

    def save(self, context: ProjectContext, markdown: str | None = None) -> ProjectContext:
        markdown = markdown or render_context_markdown(context)
        metadata = {
            "schema_version": PAGE_META_SCHEMA_VERSION,
            "page_kind": "context",
            "context": context.model_dump(mode="json"),
            "markdown": markdown,
        }
        body = build_page_body(self.CONTEXT_TITLE, metadata, markdown)
        page = self._find_page(self.CONTEXT_TITLE)
        if page is None:
            created = _create_page(
                self.client,
                space_key=self.space_key,
                parent_page_id=self.parent_page_id,
                title=self.CONTEXT_TITLE,
                body=body,
            )
            page = created if created.get("version") else _get_page(self.client, created["id"])
        else:
            updated = _update_page(self.client, page=page, title=self.CONTEXT_TITLE, body=body)
            page = updated if updated.get("version") else _get_page(self.client, page["id"])
        _upsert_page_metadata_property(self.client, page["id"], metadata)
        return context

    def _find_page(self, title: str) -> dict | None:
        for result in _list_child_pages(self.client, self.parent_page_id):
            if result.get("title") != title:
                continue
            metadata = _page_metadata(self.client, result)
            if not metadata or metadata.get("page_kind") in {None, "context"}:
                return result
        return None

    def _bootstrap_context_page(self) -> ProjectContext:
        if self.bootstrap_store is None:
            raise ValueError("Confluence context page not found and no bootstrap store was provided.")
        context = self.bootstrap_store.load()
        self.save(context, self.bootstrap_store.load_markdown())
        return context

    def _bootstrap_context_markdown(self) -> str:
        context = self._bootstrap_context_page()
        return render_context_markdown(context)


class AtlassianArtifactStore(ArtifactStore):
    def __init__(self, client: ConfluenceApiClient, *, space_key: str, parent_page_id: str) -> None:
        self.client = client
        self.space_key = space_key
        self.parent_page_id = parent_page_id

    def list(self) -> list[Artifact]:
        artifacts: list[Artifact] = []
        for page in _list_child_pages(self.client, self.parent_page_id):
            artifact = self._artifact_from_page(page)
            if artifact is not None:
                artifacts.append(artifact)
        return sorted(artifacts, key=lambda artifact: artifact.created_at, reverse=True)

    def get(self, artifact_id: str) -> Artifact | None:
        page = self._find_page_by_artifact_id(artifact_id)
        if page is None:
            return None
        return self._artifact_from_page(page)

    def save(self, artifact: Artifact) -> Artifact:
        title = f"[{artifact.task_id}] {artifact.title}"
        page = self._resolve_page_for_artifact(artifact)
        if page is None:
            created = _create_page(
                self.client,
                space_key=self.space_key,
                parent_page_id=self.parent_page_id,
                title=title,
                body=build_page_body(
                    title,
                    {
                        "schema_version": PAGE_META_SCHEMA_VERSION,
                        "page_kind": "artifact",
                        "artifact": artifact.model_dump(mode="json"),
                    },
                    render_artifact_page_markdown(artifact),
                ),
            )
            page = created if created.get("version") else _get_page(self.client, created["id"])

        stored_path = page_url(self.client.confluence_base_url, page["id"])
        stored_artifact = artifact.model_copy(update={"path": stored_path})
        metadata = {
            "schema_version": PAGE_META_SCHEMA_VERSION,
            "page_kind": "artifact",
            "artifact": stored_artifact.model_dump(mode="json"),
            "page": {
                "id": page["id"],
                "url": stored_path,
                "space_key": self.space_key,
                "parent_page_id": self.parent_page_id,
                "title": title,
            },
        }
        body = build_page_body(title, metadata, render_artifact_page_markdown(stored_artifact))
        if _page_storage_value(page) != body or page.get("title") != title:
            updated = _update_page(self.client, page=page, title=title, body=body)
            page = updated if updated.get("version") else _get_page(self.client, page["id"])
        _upsert_page_metadata_property(self.client, page["id"], metadata)
        return stored_artifact

    def _find_page_by_artifact_id(self, artifact_id: str) -> dict | None:
        for page in _list_child_pages(self.client, self.parent_page_id):
            metadata = _page_metadata(self.client, page)
            artifact_payload = metadata.get("artifact") or {}
            if artifact_payload.get("id") == artifact_id:
                return page
        return None

    def _artifact_from_page(self, page: dict) -> Artifact | None:
        metadata = _page_metadata(self.client, page)
        artifact_payload = metadata.get("artifact")
        if not artifact_payload:
            return None
        try:
            artifact = Artifact.model_validate(artifact_payload)
        except ValidationError:
            return None
        return artifact.model_copy(update={"path": page_url(self.client.confluence_base_url, page["id"])})

    def _resolve_page_for_artifact(self, artifact: Artifact) -> dict | None:
        page_id = _page_id_from_artifact_path(artifact.path)
        if page_id is not None:
            try:
                page = _get_page(self.client, page_id)
            except ValueError:
                page = None
            if page is not None:
                metadata = _page_metadata(self.client, page)
                artifact_payload = metadata.get("artifact") or {}
                if artifact_payload.get("id") == artifact.id:
                    return page
        return self._find_page_by_artifact_id(artifact.id)


def _page_storage_value(page: dict) -> str:
    return str(page.get("body", {}).get("storage", {}).get("value") or "")


def _page_metadata(client: ConfluenceApiClient, page: dict) -> dict:
    metadata = parse_page_metadata(_page_storage_value(page))
    if metadata:
        return metadata
    page_id = str(page.get("id") or "")
    if not page_id:
        return {}
    return _load_page_metadata_property(client, page_id)


def _load_page_metadata_property(client: ConfluenceApiClient, page_id: str) -> dict:
    try:
        payload = client.confluence_json("GET", f"/rest/api/content/{page_id}/property/{CONFLUENCE_META_PROPERTY_KEY}")
    except ValueError as exc:
        if _is_not_found_error(exc):
            return {}
        raise
    value = payload.get("value")
    return value if isinstance(value, dict) else {}


def _upsert_page_metadata_property(client: ConfluenceApiClient, page_id: str, metadata: dict) -> None:
    property_path = f"/rest/api/content/{page_id}/property/{CONFLUENCE_META_PROPERTY_KEY}"
    try:
        existing = client.confluence_json("GET", property_path)
    except ValueError as exc:
        if not _is_not_found_error(exc):
            raise
        client.confluence_json(
            "POST",
            f"/rest/api/content/{page_id}/property",
            {"key": CONFLUENCE_META_PROPERTY_KEY, "value": metadata},
        )
        return
    version_number = int(existing.get("version", {}).get("number") or 1)
    client.confluence_json(
        "PUT",
        property_path,
        {
            "key": CONFLUENCE_META_PROPERTY_KEY,
            "value": metadata,
            "version": {"number": version_number + 1},
        },
    )


def _page_id_from_artifact_path(path: str) -> str | None:
    if "://" not in path:
        return None
    parsed_path = parse.urlparse(path)
    page_ids = parse.parse_qs(parsed_path.query).get("pageId") or []
    if not page_ids:
        return None
    page_id = page_ids[0]
    return page_id if page_id.isdigit() else None


def _list_child_pages(client: ConfluenceApiClient, parent_page_id: str) -> list[dict]:
    pages: list[dict] = []
    start = 0
    while True:
        payload = client.confluence_json(
            "GET",
            f"/rest/api/content/{parent_page_id}/child/page?limit={CONFLUENCE_PAGE_BATCH_SIZE}&start={start}&expand=body.storage,version",
        )
        results = payload.get("results", [])
        pages.extend(results)
        if len(results) < CONFLUENCE_PAGE_BATCH_SIZE:
            break
        start += len(results)
    return pages


def _create_page(
    client: ConfluenceApiClient,
    *,
    space_key: str,
    parent_page_id: str,
    title: str,
    body: str,
) -> dict:
    return client.confluence_json(
        "POST",
        "/rest/api/content?expand=body.storage,version",
        {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "ancestors": [{"id": parent_page_id}],
            "body": {"storage": {"value": body, "representation": "storage"}},
        },
    )


def _update_page(client: ConfluenceApiClient, *, page: dict, title: str, body: str) -> dict:
    version_number = int(page.get("version", {}).get("number") or 1)
    response = client.confluence_json(
        "PUT",
        f"/rest/api/content/{page['id']}",
        {
            "id": page["id"],
            "type": "page",
            "title": title,
            "version": {"number": version_number + 1},
            "body": {"storage": {"value": body, "representation": "storage"}},
        },
    )
    if response:
        return response
    return {
        "id": page["id"],
        "title": title,
        "version": {"number": version_number + 1},
        "body": {"storage": {"value": body}},
    }


def _get_page(client: ConfluenceApiClient, page_id: str) -> dict:
    return client.confluence_json("GET", f"/rest/api/content/{page_id}?expand=body.storage,version")


def _latest_event_key(task: Task) -> str | None:
    if not task.history:
        return None
    latest = task.history[-1]
    return f"{latest.timestamp}:{latest.event_type}:{latest.message}"


def _is_not_found_error(exc: ValueError) -> bool:
    if isinstance(exc, AtlassianApiError):
        return exc.status_code == 404
    message = str(exc).casefold()
    return "api error 404" in message or message.startswith("issue not found:") or message.startswith("property not found:")


def _matches_status(value: str, candidates: tuple[str, ...]) -> bool:
    normalized_value = _normalize_status_name(value)
    return any(normalized_value == _normalize_status_name(candidate) for candidate in candidates)


def _normalize_status_name(value: str) -> str:
    return " ".join(value.casefold().split())


def _transition_names(transitions: list[dict]) -> list[str]:
    names: list[str] = []
    for transition in transitions:
        to_name = transition.get("to", {}).get("name")
        if to_name:
            names.append(to_name)
    return names


def _status_sync_note(status: Status, jira_status_name: str) -> str | None:
    if status != Status.REVISION_NEEDED:
        return None
    if _matches_status(jira_status_name, ("In Progress", "Doing", "Development", "진행 중")):
        return 'Internal status revision_needed is represented in Jira as "In Progress".'
    return (
        f'Internal status revision_needed was stored in the issue property, and Jira status '
        f'remains "{jira_status_name}" because the workflow does not expose a dedicated rework step.'
    )


def _category_fallback_note(status: Status, current_name: str, target_name: str) -> str:
    if status == Status.REVISION_NEEDED:
        return _status_sync_note(status, current_name) or ""
    return (
        f'Jira does not expose a "{target_name}" transition from the current workflow, so the issue '
        f'remains in "{current_name}" while the canonical task state is stored in the issue property.'
    )


def _dedupe_notes(notes: list[str]) -> str:
    unique_notes: list[str] = []
    for note in notes:
        if note not in unique_notes:
            unique_notes.append(note)
    return " ".join(unique_notes)



