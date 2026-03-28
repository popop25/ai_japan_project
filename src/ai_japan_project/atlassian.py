from __future__ import annotations

import base64
import json
from html import escape, unescape
from pathlib import Path
from urllib import error, parse, request

from .interfaces import ArtifactStore, ContextStore, TaskStore
from .models import Artifact, ProjectContext, Status, Task
from .renderers import render_context_markdown
from .storage import LocalContextStore

TASK_PROPERTY_KEY = "ai_japan_project.task"
PAGE_META_PREFIX = "<!-- AJP_META:"
PAGE_META_SUFFIX = "-->"
JIRA_LABEL = "ai-japan-project"


class AtlassianClient:
    def __init__(
        self,
        *,
        email: str,
        api_token: str,
        jira_base_url: str,
        confluence_base_url: str,
    ) -> None:
        auth_pair = f"{email}:{api_token}".encode("utf-8")
        self.auth_header = "Basic " + base64.b64encode(auth_pair).decode("ascii")
        self.jira_base_url = jira_base_url.rstrip("/")
        self.confluence_base_url = confluence_base_url.rstrip("/")

    def jira_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        return self._json_request(self.jira_base_url, method, path, payload)

    def confluence_json(self, method: str, path: str, payload: dict | None = None) -> dict:
        return self._json_request(self.confluence_base_url, method, path, payload)

    def _json_request(self, base_url: str, method: str, path: str, payload: dict | None = None) -> dict:
        url = f"{base_url}{path}"
        data = None
        headers = {
            "Authorization": self.auth_header,
            "Accept": "application/json",
        }
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = request.Request(url, data=data, headers=headers, method=method.upper())
        try:
            with request.urlopen(req, timeout=30) as response:
                text = response.read().decode("utf-8")
                return json.loads(text) if text else {}
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"Atlassian API error {exc.code} for {method} {path}: {body}") from exc


def task_status_to_jira(status: Status) -> str:
    if status == Status.PENDING:
        return "To Do"
    if status == Status.IN_PROGRESS:
        return "In Progress"
    if status == Status.REVISION_NEEDED:
        return "In Progress"
    if status == Status.REVIEW_REQUESTED:
        return "In Review"
    return "Done"


def render_issue_description(task: Task) -> dict:
    lines = [
        f"Task ID: {task.id}",
        f"Role: {task.role}",
        f"Deliverable: {task.deliverable}",
        f"Status: {task.status.value}",
    ]
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
    if not storage_value.startswith(PAGE_META_PREFIX):
        return {}
    end = storage_value.find(PAGE_META_SUFFIX)
    if end == -1:
        return {}
    raw_json = storage_value[len(PAGE_META_PREFIX):end]
    return json.loads(unescape(raw_json))


def markdown_to_storage(markdown: str) -> str:
    blocks: list[str] = []
    lines = markdown.splitlines()
    in_list = False
    for raw_line in lines:
        line = raw_line.rstrip()
        if not line:
            if in_list:
                blocks.append("</ul>")
                in_list = False
            continue
        if line.startswith("# "):
            if in_list:
                blocks.append("</ul>")
                in_list = False
            blocks.append(f"<h2>{escape(line[2:])}</h2>")
            continue
        if line.startswith("## "):
            if in_list:
                blocks.append("</ul>")
                in_list = False
            blocks.append(f"<h3>{escape(line[3:])}</h3>")
            continue
        if line.startswith("- "):
            if not in_list:
                blocks.append("<ul>")
                in_list = True
            blocks.append(f"<li>{escape(line[2:])}</li>")
            continue
        if in_list:
            blocks.append("</ul>")
            in_list = False
        blocks.append(f"<p>{escape(line)}</p>")
    if in_list:
        blocks.append("</ul>")
    return "".join(blocks)


def page_url(base_url: str, page_id: str) -> str:
    return f"{base_url}/pages/viewpage.action?pageId={page_id}"


def update_task_ref(task: Task, **refs: str) -> Task:
    merged = {**task.refs, **refs}
    return task.model_copy(update={"refs": merged})


class AtlassianTaskStore(TaskStore):
    def __init__(self, client: AtlassianClient, project_key: str) -> None:
        self.client = client
        self.project_key = project_key

    def list(self) -> list[Task]:
        jql = parse.quote(f'project = "{self.project_key}" AND labels = "{JIRA_LABEL}" ORDER BY updated DESC')
        payload = self.client.jira_json("GET", f"/rest/api/3/search?jql={jql}&maxResults=100&fields=summary,status")
        tasks: list[Task] = []
        for issue in payload.get("issues", []):
            task = self._load_task_from_issue(issue)
            if task is not None:
                tasks.append(task)
        return tasks

    def get(self, task_id: str) -> Task | None:
        for task in self.list():
            if task.id == task_id:
                return task
        return None

    def save(self, task: Task) -> Task:
        issue_key = task.refs.get("jira_issue_key")
        previous_task = self.get(task.id)
        if issue_key:
            self._update_issue(issue_key, task)
        else:
            issue_key = self._create_issue(task)
            task = update_task_ref(task, jira_issue_key=issue_key)
        self._save_property(issue_key, task)
        self._sync_status(issue_key, task.status)
        if previous_task is None or _latest_event_key(previous_task) != _latest_event_key(task):
            self._add_comment(issue_key, task.history[-1].message if task.history else f"Task updated: {task.title}")
        return task

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
        except ValueError:
            return None
        task = Task.model_validate(payload.get("value") or {})
        return update_task_ref(task, jira_issue_key=issue_key)

    def _sync_status(self, issue_key: str, status: Status) -> None:
        target_name = task_status_to_jira(status)
        issue = self.client.jira_json("GET", f"/rest/api/3/issue/{issue_key}?fields=status")
        current_name = issue["fields"]["status"]["name"]
        if current_name == target_name:
            return
        transitions = self.client.jira_json("GET", f"/rest/api/3/issue/{issue_key}/transitions")
        for transition in transitions.get("transitions", []):
            if transition.get("to", {}).get("name") == target_name:
                self.client.jira_json(
                    "POST",
                    f"/rest/api/3/issue/{issue_key}/transitions",
                    {"transition": {"id": transition["id"]}},
                )
                return
        raise ValueError(f"No Jira transition available from {current_name} to {target_name} for {issue_key}")

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
        client: AtlassianClient,
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
            if self.bootstrap_store is None:
                raise ValueError("Confluence context page not found and no bootstrap store was provided.")
            context = self.bootstrap_store.load()
            self.save(context, render_context_markdown(context))
            return context
        metadata = parse_page_metadata(page["body"]["storage"]["value"])
        return ProjectContext.model_validate(metadata["context"])

    def load_markdown(self) -> str:
        return render_context_markdown(self.load())

    def save(self, context: ProjectContext, markdown: str | None = None) -> ProjectContext:
        markdown = markdown or render_context_markdown(context)
        body = build_page_body(self.CONTEXT_TITLE, {"context": context.model_dump(mode="json")}, markdown)
        page = self._find_page(self.CONTEXT_TITLE)
        if page is None:
            self.client.confluence_json(
                "POST",
                "/wiki/rest/api/content",
                {
                    "type": "page",
                    "title": self.CONTEXT_TITLE,
                    "space": {"key": self.space_key},
                    "ancestors": [{"id": self.parent_page_id}],
                    "body": {"storage": {"value": body, "representation": "storage"}},
                },
            )
        else:
            self.client.confluence_json(
                "PUT",
                f"/wiki/rest/api/content/{page['id']}",
                {
                    "id": page["id"],
                    "type": "page",
                    "title": self.CONTEXT_TITLE,
                    "version": {"number": page["version"]["number"] + 1},
                    "body": {"storage": {"value": body, "representation": "storage"}},
                },
            )
        return context

    def _find_page(self, title: str) -> dict | None:
        encoded_title = parse.quote(title)
        payload = self.client.confluence_json(
            "GET",
            f"/wiki/rest/api/content?spaceKey={self.space_key}&title={encoded_title}&expand=body.storage,version",
        )
        for result in payload.get("results", []):
            if result.get("title") == title:
                return result
        return None


class AtlassianArtifactStore(ArtifactStore):
    def __init__(self, client: AtlassianClient, *, space_key: str, parent_page_id: str) -> None:
        self.client = client
        self.space_key = space_key
        self.parent_page_id = parent_page_id

    def list(self) -> list[Artifact]:
        payload = self.client.confluence_json(
            "GET",
            f"/wiki/rest/api/content/{self.parent_page_id}/child/page?limit=200&expand=body.storage,version",
        )
        artifacts: list[Artifact] = []
        for page in payload.get("results", []):
            metadata = parse_page_metadata(page["body"]["storage"]["value"])
            artifact_payload = metadata.get("artifact")
            if not artifact_payload:
                continue
            artifact = Artifact.model_validate(artifact_payload)
            artifacts.append(artifact.model_copy(update={"path": page_url(self.client.confluence_base_url, page["id"])}))
        return sorted(artifacts, key=lambda artifact: artifact.created_at, reverse=True)

    def get(self, artifact_id: str) -> Artifact | None:
        for artifact in self.list():
            if artifact.id == artifact_id:
                return artifact
        return None

    def save(self, artifact: Artifact) -> Artifact:
        title = f"[{artifact.task_id}] {artifact.title}"
        body = build_page_body(title, {"artifact": artifact.model_dump(mode="json")}, artifact.content)
        page = self._find_page_by_artifact_id(artifact.id)
        if page is None:
            created = self.client.confluence_json(
                "POST",
                "/wiki/rest/api/content",
                {
                    "type": "page",
                    "title": title,
                    "space": {"key": self.space_key},
                    "ancestors": [{"id": self.parent_page_id}],
                    "body": {"storage": {"value": body, "representation": "storage"}},
                },
            )
            return artifact.model_copy(update={"path": page_url(self.client.confluence_base_url, created["id"])} )
        self.client.confluence_json(
            "PUT",
            f"/wiki/rest/api/content/{page['id']}",
            {
                "id": page["id"],
                "type": "page",
                "title": title,
                "version": {"number": page["version"]["number"] + 1},
                "body": {"storage": {"value": body, "representation": "storage"}},
            },
        )
        return artifact.model_copy(update={"path": page_url(self.client.confluence_base_url, page["id"])} )

    def _find_page_by_artifact_id(self, artifact_id: str) -> dict | None:
        payload = self.client.confluence_json(
            "GET",
            f"/wiki/rest/api/content/{self.parent_page_id}/child/page?limit=200&expand=body.storage,version",
        )
        for page in payload.get("results", []):
            metadata = parse_page_metadata(page["body"]["storage"]["value"])
            artifact_payload = metadata.get("artifact") or {}
            if artifact_payload.get("id") == artifact_id:
                return page
        return None


def _latest_event_key(task: Task) -> str | None:
    if not task.history:
        return None
    latest = task.history[-1]
    return f"{latest.timestamp}:{latest.event_type}:{latest.message}"
