from __future__ import annotations

from pathlib import Path

import yaml

from .models import Artifact, ProjectContext, RunSession, Task
from .paths import (
    ARTIFACTS_DIR,
    CONTEXT_MARKDOWN_PATH,
    CONTEXT_YAML_PATH,
    RUNS_DIR,
    TASKS_DIR,
)
from .renderers import render_context_markdown


def ensure_runtime_dirs() -> None:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def save_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)


def split_frontmatter(document: str) -> tuple[dict, str]:
    stripped = document.strip()
    if not stripped.startswith("---"):
        return {}, document
    lines = document.splitlines()
    closing = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            closing = index
            break
    if closing is None:
        return {}, document
    frontmatter = yaml.safe_load("\n".join(lines[1:closing])) or {}
    body = "\n".join(lines[closing + 1 :]).lstrip("\n")
    return frontmatter, body


def compose_frontmatter(frontmatter: dict, body: str) -> str:
    rendered = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    body = body.strip("\n")
    if body:
        return f"---\n{rendered}\n---\n{body}\n"
    return f"---\n{rendered}\n---\n"


class LocalContextStore:
    def __init__(
        self,
        yaml_path: Path = CONTEXT_YAML_PATH,
        markdown_path: Path = CONTEXT_MARKDOWN_PATH,
    ) -> None:
        self.yaml_path = yaml_path
        self.markdown_path = markdown_path

    def load(self) -> ProjectContext:
        return ProjectContext.model_validate(load_yaml(self.yaml_path))

    def load_markdown(self) -> str:
        if not self.markdown_path.exists():
            return render_context_markdown(self.load())
        return self.markdown_path.read_text(encoding="utf-8")

    def save(self, context: ProjectContext, markdown: str | None = None) -> ProjectContext:
        save_yaml(self.yaml_path, context.model_dump(mode="json"))
        self.markdown_path.write_text(
            markdown or render_context_markdown(context),
            encoding="utf-8",
        )
        return context


class LocalTaskStore:
    def __init__(self, base_dir: Path = TASKS_DIR) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[Task]:
        tasks = [Task.model_validate(load_yaml(path)) for path in self.base_dir.glob("*.yaml")]
        return sorted(tasks, key=lambda task: task.updated_at, reverse=True)

    def get(self, task_id: str) -> Task | None:
        path = self.base_dir / f"{task_id}.yaml"
        if not path.exists():
            return None
        return Task.model_validate(load_yaml(path))

    def save(self, task: Task) -> Task:
        save_yaml(self.base_dir / f"{task.id}.yaml", task.model_dump(mode="json"))
        return task


class LocalArtifactStore:
    def __init__(self, base_dir: Path = ARTIFACTS_DIR) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[Artifact]:
        artifacts = []
        for path in self.base_dir.glob("*.md"):
            frontmatter, body = split_frontmatter(path.read_text(encoding="utf-8"))
            if not frontmatter:
                continue
            artifacts.append(
                Artifact.model_validate(
                    {
                        **frontmatter,
                        "path": str(path),
                        "content": body,
                    }
                )
            )
        return sorted(artifacts, key=lambda artifact: artifact.created_at, reverse=True)

    def get(self, artifact_id: str) -> Artifact | None:
        path = self.base_dir / f"{artifact_id}.md"
        if not path.exists():
            return None
        frontmatter, body = split_frontmatter(path.read_text(encoding="utf-8"))
        return Artifact.model_validate({**frontmatter, "path": str(path), "content": body})

    def save(self, artifact: Artifact) -> Artifact:
        path = self.base_dir / f"{artifact.id}.md"
        frontmatter = {
            "id": artifact.id,
            "task_id": artifact.task_id,
            "kind": artifact.kind,
            "title": artifact.title,
            "created_at": artifact.created_at,
        }
        body = artifact.content
        embedded_meta, embedded_body = split_frontmatter(artifact.content)
        if embedded_meta:
            frontmatter.update(embedded_meta)
            body = embedded_body
        path.write_text(compose_frontmatter(frontmatter, body), encoding="utf-8")
        return artifact.model_copy(update={"path": str(path), "content": body})


class LocalRunStore:
    def __init__(self, base_dir: Path = RUNS_DIR) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def list_for_task(self, task_id: str) -> list[RunSession]:
        runs = []
        for path in self.base_dir.glob("*.yaml"):
            payload = load_yaml(path)
            if payload.get("task_id") == task_id:
                runs.append(RunSession.model_validate(payload))
        return sorted(runs, key=lambda run: run.updated_at, reverse=True)

    def save(self, run: RunSession) -> RunSession:
        save_yaml(self.base_dir / f"{run.id}.yaml", run.model_dump(mode="json"))
        return run

    def save_packet(self, packet_name: str, content: str) -> Path:
        path = self.base_dir / packet_name
        path.write_text(content, encoding="utf-8")
        return path

    def load_packet(self, packet_name: str) -> str:
        return (self.base_dir / packet_name).read_text(encoding="utf-8")