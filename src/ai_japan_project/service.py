from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .models import (
    Artifact,
    DashboardActivity,
    DashboardData,
    IngestCriticRequest,
    IngestPMRequest,
    ProjectContext,
    Review,
    RunSession,
    Status,
    Task,
    TaskDetail,
    TaskEvent,
    WorkPacket,
)
from .renderers import (
    render_context_markdown,
    render_critic_packet,
    render_pm_packet,
    render_review_document,
)
from .storage import (
    LocalArtifactStore,
    LocalContextStore,
    LocalRunStore,
    LocalTaskStore,
    ensure_runtime_dirs,
    split_frontmatter,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:10]}"


class ProjectService:
    def __init__(
        self,
        context_store: LocalContextStore | None = None,
        task_store: LocalTaskStore | None = None,
        artifact_store: LocalArtifactStore | None = None,
        run_store: LocalRunStore | None = None,
    ) -> None:
        ensure_runtime_dirs()
        self.context_store = context_store or LocalContextStore()
        self.task_store = task_store or LocalTaskStore()
        self.artifact_store = artifact_store or LocalArtifactStore()
        self.run_store = run_store or LocalRunStore()
        self._bootstrap_context_markdown()

    @property
    def project_root(self) -> Path:
        return self.context_store.yaml_path.parent

    @property
    def repo_root(self) -> Path:
        return self.project_root.parent

    def _bootstrap_context_markdown(self) -> None:
        if not self.context_store.markdown_path.exists():
            context = self.context_store.load()
            self.context_store.save(context, render_context_markdown(context))

    def get_context(self) -> tuple[ProjectContext, str]:
        return self.context_store.load(), self.context_store.load_markdown()

    def save_context(self, context: ProjectContext) -> tuple[ProjectContext, str]:
        markdown = render_context_markdown(context)
        saved = self.context_store.save(context, markdown)
        return saved, markdown

    def list_tasks(self) -> list[Task]:
        return self.task_store.list()

    def create_requirements_task(self, title: str | None = None) -> TaskDetail:
        timestamp = utc_now()
        task = Task(
            id=make_id("task"),
            title=title or "요구사항 정의서 초안 작성",
            role="pm",
            deliverable="requirements_draft",
            status=Status.PENDING,
            refs={
                "context": "project/03_context.md",
                "pm_skill": "project/skills/pm.md",
                "critic_skill": "project/skills/critic.md",
            },
            created_at=timestamp,
            updated_at=timestamp,
            history=[
                TaskEvent(
                    timestamp=timestamp,
                    event_type="task_created",
                    actor="system",
                    message="요구사항 정의서 작성을 위한 PM task가 생성되었습니다.",
                    status=Status.PENDING,
                )
            ],
        )
        self.task_store.save(task)
        return self.get_task_detail(task.id)

    def get_task_detail(self, task_id: str) -> TaskDetail:
        task = self._require_task(task_id)
        runs = self.run_store.list_for_task(task_id)
        artifacts = [artifact for artifact in self.artifact_store.list() if artifact.task_id == task_id]
        pm_packet = self._load_latest_packet(runs, "pm")
        critic_packet = self._load_latest_packet(runs, "critic")
        review = self._load_latest_review(artifacts, task_id)
        return TaskDetail(
            task=task,
            runs=runs,
            artifacts=artifacts,
            pm_packet=pm_packet,
            critic_packet=critic_packet,
            review=review,
        )

    def dispatch_pm(self, task_id: str) -> TaskDetail:
        task = self._require_task(task_id)
        if task.status not in {Status.PENDING, Status.REVISION_NEEDED}:
            raise ValueError("PM packet can only be generated from pending or revision_needed.")

        _, context_markdown = self.get_context()
        skill_text = self._read_repo_text(task.refs["pm_skill"])
        packet_content = render_pm_packet(task, context_markdown, skill_text)
        packet_id = make_id("packet")
        packet_path = self.run_store.save_packet(f"{packet_id}.md", packet_content)
        timestamp = utc_now()
        run = RunSession(
            id=make_id("run"),
            task_id=task.id,
            stage="pm",
            status="packet_generated",
            packet_id=packet_id,
            packet_path=str(packet_path),
            created_at=timestamp,
            updated_at=timestamp,
        )
        self.run_store.save(run)
        updated = task.model_copy(
            update={
                "status": Status.IN_PROGRESS,
                "latest_run_id": run.id,
                "updated_at": timestamp,
                "history": task.history
                + [
                    TaskEvent(
                        timestamp=timestamp,
                        event_type="pm_packet_generated",
                        actor="system",
                        message="PM 에이전트용 work packet이 생성되었습니다.",
                        status=Status.IN_PROGRESS,
                    )
                ],
            }
        )
        self.task_store.save(updated)
        return self.get_task_detail(task.id)

    def ingest_pm(self, task_id: str, request: IngestPMRequest | str, title: str | None = None) -> TaskDetail:
        task = self._require_task(task_id)
        if task.status != Status.IN_PROGRESS:
            raise ValueError("PM result can only be ingested while the task is in progress.")

        if isinstance(request, IngestPMRequest):
            content = request.content
            artifact_title = request.title
        else:
            content = request
            artifact_title = title
        if not content.strip():
            raise ValueError("PM result cannot be empty.")

        timestamp = utc_now()
        latest_run = self._require_latest_run(task.id, "pm")
        artifact = Artifact(
            id=make_id("artifact"),
            task_id=task.id,
            kind="pm_output",
            title=artifact_title or "요구사항 정의서 초안",
            created_at=timestamp,
            path="",
            content=content.strip() + "\n",
        )
        saved_artifact = self.artifact_store.save(artifact)
        self.run_store.save(
            latest_run.model_copy(
                update={
                    "status": "result_ingested",
                    "output_artifact_id": saved_artifact.id,
                    "updated_at": timestamp,
                }
            )
        )
        updated = task.model_copy(
            update={
                "artifact_ids": task.artifact_ids + [saved_artifact.id],
                "updated_at": timestamp,
                "history": task.history
                + [
                    TaskEvent(
                        timestamp=timestamp,
                        event_type="pm_result_ingested",
                        actor="human",
                        message="PM 에이전트 산출물이 업로드되었습니다.",
                        status=Status.IN_PROGRESS,
                    )
                ],
            }
        )
        self.task_store.save(updated)
        return self.get_task_detail(task.id)

    def dispatch_critic(self, task_id: str) -> TaskDetail:
        task = self._require_task(task_id)
        pm_artifact = self._require_latest_artifact(task, "pm_output")
        _, context_markdown = self.get_context()
        critic_skill = self._read_repo_text(task.refs["critic_skill"])
        packet_content = render_critic_packet(task, context_markdown, critic_skill, pm_artifact.content)
        packet_id = make_id("packet")
        packet_path = self.run_store.save_packet(f"{packet_id}.md", packet_content)
        timestamp = utc_now()
        run = RunSession(
            id=make_id("run"),
            task_id=task.id,
            stage="critic",
            status="packet_generated",
            packet_id=packet_id,
            packet_path=str(packet_path),
            created_at=timestamp,
            updated_at=timestamp,
        )
        self.run_store.save(run)
        updated = task.model_copy(
            update={
                "latest_run_id": run.id,
                "updated_at": timestamp,
                "history": task.history
                + [
                    TaskEvent(
                        timestamp=timestamp,
                        event_type="critic_packet_generated",
                        actor="system",
                        message="Critic 에이전트용 review packet이 생성되었습니다.",
                        status=Status.IN_PROGRESS,
                    )
                ],
            }
        )
        self.task_store.save(updated)
        return self.get_task_detail(task.id)

    def ingest_critic(self, task_id: str, request: IngestCriticRequest | str) -> TaskDetail:
        task = self._require_task(task_id)
        if isinstance(request, IngestCriticRequest):
            review_markdown = request.review_markdown
        else:
            review_markdown = request
        if not review_markdown.strip():
            raise ValueError("Critic review cannot be empty.")

        latest_run = self._require_latest_run(task.id, "critic")
        frontmatter, notes = split_frontmatter(review_markdown)
        if not frontmatter:
            raise ValueError("Critic review must include YAML front matter.")
        verdict = frontmatter.get("verdict")
        if verdict not in {"approve", "revise"}:
            raise ValueError("Critic verdict must be approve or revise.")

        timestamp = utc_now()
        review = Review(
            id=make_id("review"),
            task_id=task.id,
            verdict=verdict,
            summary=(frontmatter.get("summary") or "").strip() or "총평이 제공되지 않았습니다.",
            missing_items=list(frontmatter.get("missing_items") or []),
            recommended_changes=list(frontmatter.get("recommended_changes") or []),
            artifact_id="",
            created_at=timestamp,
        )
        review_artifact = Artifact(
            id=make_id("artifact"),
            task_id=task.id,
            kind="critic_review",
            title="Critic Review",
            created_at=timestamp,
            path="",
            content=render_review_document(review, notes),
        )
        saved_artifact = self.artifact_store.save(review_artifact)
        self.run_store.save(
            latest_run.model_copy(
                update={
                    "status": "result_ingested",
                    "output_artifact_id": saved_artifact.id,
                    "updated_at": timestamp,
                }
            )
        )
        next_status = Status.REVIEW_REQUESTED if verdict == "approve" else Status.REVISION_NEEDED
        review_message = (
            "Critic이 승인했습니다. 사람 검토 요청 단계로 이동합니다."
            if verdict == "approve"
            else "Critic이 수정 필요를 반환했습니다. PM 재작업이 필요합니다."
        )
        updated = task.model_copy(
            update={
                "status": next_status,
                "artifact_ids": task.artifact_ids + [saved_artifact.id],
                "updated_at": timestamp,
                "history": task.history
                + [
                    TaskEvent(
                        timestamp=timestamp,
                        event_type="critic_review_ingested",
                        actor="human",
                        message=review_message,
                        status=next_status,
                    )
                ],
            }
        )
        self.task_store.save(updated)
        return self.get_task_detail(task.id)

    def get_artifact(self, artifact_id: str) -> Artifact | None:
        return self.artifact_store.get(artifact_id)

    def get_dashboard(self) -> DashboardData:
        context, _ = self.get_context()
        tasks = self.list_tasks()
        status_counts = {status.value: 0 for status in Status}
        for task in tasks:
            status_counts[task.status.value] += 1
        latest_artifacts = self.artifact_store.list()[:5]
        activities: list[DashboardActivity] = []
        for task in tasks:
            for event in task.history:
                activities.append(
                    DashboardActivity(
                        task_id=task.id,
                        task_title=task.title,
                        timestamp=event.timestamp,
                        event_type=event.event_type,
                        message=event.message,
                        status=event.status,
                    )
                )
        activities.sort(key=lambda item: item.timestamp, reverse=True)
        return DashboardData(
            context=context,
            active_tasks=tasks[:5],
            recent_activity=activities[:12],
            latest_artifacts=latest_artifacts,
            status_counts=status_counts,
        )

    def _require_task(self, task_id: str) -> Task:
        task = self.task_store.get(task_id)
        if task is None:
            raise ValueError(f"Task not found: {task_id}")
        return task

    def _require_latest_run(self, task_id: str, stage: str) -> RunSession:
        for run in self.run_store.list_for_task(task_id):
            if run.stage == stage:
                return run
        raise ValueError(f"No {stage} run found for task {task_id}")

    def _require_latest_artifact(self, task: Task, kind: str) -> Artifact:
        for artifact_id in reversed(task.artifact_ids):
            artifact = self.artifact_store.get(artifact_id)
            if artifact and artifact.kind == kind:
                return artifact
        raise ValueError(f"No {kind} artifact found for task {task.id}")

    def _safe_display_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.repo_root))
        except ValueError:
            return str(path)

    def _load_latest_packet(self, runs: list[RunSession], stage: str) -> WorkPacket | None:
        for run in runs:
            if run.stage != stage:
                continue
            packet_path = Path(run.packet_path)
            return WorkPacket(
                id=run.packet_id,
                task_id=run.task_id,
                stage=run.stage,
                agent_role="PM Agent" if run.stage == "pm" else "Critic Agent",
                title=f"{run.stage.upper()} work packet",
                created_at=run.created_at,
                input_refs=[
                    "project/03_context.md",
                    "project/skills/pm.md" if run.stage == "pm" else "project/skills/critic.md",
                ],
                output_contract=[],
                handoff_instructions="Copy this packet into Codex or Claude Code, then paste the result back into the app.",
                content=self.run_store.load_packet(packet_path.name),
                path=self._safe_display_path(packet_path),
            )
        return None

    def _load_latest_review(self, artifacts: list[Artifact], task_id: str) -> Review | None:
        for artifact in artifacts:
            if artifact.kind != "critic_review":
                continue
            raw_text = Path(artifact.path).read_text(encoding="utf-8")
            frontmatter, _ = split_frontmatter(raw_text)
            if not frontmatter:
                continue
            return Review(
                id=make_id("review_preview"),
                task_id=task_id,
                verdict=frontmatter.get("verdict", "revise"),
                summary=frontmatter.get("summary", ""),
                missing_items=list(frontmatter.get("missing_items") or []),
                recommended_changes=list(frontmatter.get("recommended_changes") or []),
                artifact_id=artifact.id,
                created_at=artifact.created_at,
            )
        return None

    def _read_repo_text(self, relative_path: str) -> str:
        return (self.repo_root / relative_path).read_text(encoding="utf-8")