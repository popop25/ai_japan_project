from __future__ import annotations

from pathlib import Path

from ai_japan_project.models import Status


def parse_multiline(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def get_latest_artifact(detail, kind: str):
    for artifact in detail.artifacts:
        if artifact.kind == kind:
            return artifact
    return None


def get_artifact_source(artifact) -> str:
    path = Path(str(artifact.path))
    if artifact.path and path.exists():
        return path.read_text(encoding="utf-8")
    return artifact.content


def get_workflow_stage(detail) -> str:
    if detail is None:
        return "create_task"
    pm_output = get_latest_artifact(detail, "pm_output")
    if detail.pm_packet is None or detail.task.status in {Status.PENDING, Status.REVISION_NEEDED}:
        return "create_pm_prompt"
    if pm_output is None:
        return "ingest_pm_result"
    if detail.critic_packet is None and detail.review is None:
        return "create_critic_prompt"
    if detail.review is None:
        return "ingest_critic_review"
    return "review_outcome"


def workflow_steps(detail) -> list[dict[str, str]]:
    stage = get_workflow_stage(detail)
    order = {
        "create_task": 0,
        "create_pm_prompt": 1,
        "ingest_pm_result": 1,
        "create_critic_prompt": 2,
        "ingest_critic_review": 2,
        "review_outcome": 3,
    }[stage]
    return [
        {"index": "1", "title": "맥락 정리", "description": "프로젝트 목적과 제약을 확인합니다.", "state": "done"},
        {"index": "2", "title": "PM 초안 만들기", "description": "PM용 프롬프트를 만들고 초안을 반영합니다.", "state": "done" if order > 1 else "current" if order == 1 else "todo"},
        {"index": "3", "title": "Critic 검토", "description": "검토용 프롬프트를 만들고 리뷰를 반영합니다.", "state": "done" if order > 2 else "current" if order == 2 else "todo"},
        {"index": "4", "title": "결과 공유", "description": "최종 상태와 산출물을 확인합니다.", "state": "done" if order > 3 else "current" if order == 3 else "todo"},
    ]
