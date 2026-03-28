from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVISION_NEEDED = "revision_needed"
    REVIEW_REQUESTED = "review_requested"
    DONE = "done"


class Constraints(BaseModel):
    technical: str
    schedule: str
    other: str


class DecisionEntry(BaseModel):
    date: str
    decision: str
    reason: str


class References(BaseModel):
    jira: str
    skills: str
    notes: str


class ProjectContext(BaseModel):
    name: str
    purpose: str
    customer: str
    current_stage: str
    active_work: str
    last_updated: str
    constraints: Constraints
    next_actions: list[str] = Field(default_factory=list)
    decisions: list[DecisionEntry] = Field(default_factory=list)
    references: References


class TaskEvent(BaseModel):
    timestamp: str
    event_type: str
    actor: str
    message: str
    status: Status


class Task(BaseModel):
    id: str
    title: str
    role: Literal["pm"]
    deliverable: Literal["requirements_draft"]
    status: Status
    refs: dict[str, str]
    artifact_ids: list[str] = Field(default_factory=list)
    latest_run_id: str | None = None
    created_at: str
    updated_at: str
    history: list[TaskEvent] = Field(default_factory=list)


class WorkPacket(BaseModel):
    id: str
    task_id: str
    stage: Literal["pm", "critic"]
    agent_role: str
    title: str
    created_at: str
    input_refs: list[str] = Field(default_factory=list)
    output_contract: list[str] = Field(default_factory=list)
    handoff_instructions: str
    content: str
    path: str


class RunSession(BaseModel):
    id: str
    task_id: str
    stage: Literal["pm", "critic"]
    status: Literal["packet_generated", "result_ingested"]
    packet_id: str
    packet_path: str
    output_artifact_id: str | None = None
    created_at: str
    updated_at: str


class Artifact(BaseModel):
    id: str
    task_id: str
    kind: Literal["pm_output", "critic_review"]
    title: str
    created_at: str
    path: str
    content: str


class Review(BaseModel):
    id: str
    task_id: str
    verdict: Literal["approve", "revise"]
    summary: str
    missing_items: list[str] = Field(default_factory=list)
    recommended_changes: list[str] = Field(default_factory=list)
    artifact_id: str
    created_at: str


class DashboardActivity(BaseModel):
    task_id: str
    task_title: str
    timestamp: str
    event_type: str
    message: str
    status: Status


class DashboardData(BaseModel):
    context: ProjectContext
    active_tasks: list[Task]
    recent_activity: list[DashboardActivity]
    latest_artifacts: list[Artifact]
    status_counts: dict[str, int]


class TaskDetail(BaseModel):
    task: Task
    runs: list[RunSession]
    artifacts: list[Artifact]
    pm_packet: WorkPacket | None = None
    critic_packet: WorkPacket | None = None
    review: Review | None = None


class CreateTaskRequest(BaseModel):
    title: str | None = None


class IngestPMRequest(BaseModel):
    content: str
    title: str | None = None


class IngestCriticRequest(BaseModel):
    review_markdown: str


class DemoSeedResult(BaseModel):
    context: ProjectContext
    context_markdown_path: str


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


ConstraintSet = Constraints
ContextDecision = DecisionEntry
ProjectReferences = References
CriticReview = Review
DashboardState = DashboardData
