from __future__ import annotations

from pathlib import Path

from ai_japan_project.renderers import render_context_markdown
from ai_japan_project.service import ProjectService
from ai_japan_project.storage import (
    LocalArtifactStore,
    LocalContextStore,
    LocalRunStore,
    LocalTaskStore,
)


def seed_project(root: Path) -> Path:
    project = root / "project"
    (project / "skills").mkdir(parents=True, exist_ok=True)
    (project / "tasks").mkdir(parents=True, exist_ok=True)
    (project / "artifacts").mkdir(parents=True, exist_ok=True)
    (project / "runs").mkdir(parents=True, exist_ok=True)
    (project / "context.yaml").write_text(
        """name: Demo Project
purpose: 테스트용 PM workflow 검증
customer: 가상 고객
current_stage: 킥오프 완료
active_work: 요구사항 정의 준비
last_updated: 2026-03-28
constraints:
  technical: 로컬 파일 저장소
  schedule: 빠른 데모 구현
  other: 비개발자 시연 필요
next_actions:
  - 요구사항 정의서 작성
  - critic 검토 반영
decisions:
  - date: 2026-03-28
    decision: PM 에이전트 우선 적용
    reason: 이해하기 쉬운 산출물 중심
references:
  jira: local only
  skills: project/skills/pm.md
  notes: project/03_context.md
""",
        encoding="utf-8",
    )
    (project / "skills" / "pm.md").write_text("# PM skill", encoding="utf-8")
    (project / "skills" / "critic.md").write_text("# Critic skill", encoding="utf-8")
    context_store = LocalContextStore(
        yaml_path=project / "context.yaml",
        markdown_path=project / "03_context.md",
    )
    context = context_store.load()
    context_store.save(context, render_context_markdown(context))
    return project


def build_service(project: Path) -> ProjectService:
    return ProjectService(
        context_store=LocalContextStore(
            yaml_path=project / "context.yaml",
            markdown_path=project / "03_context.md",
        ),
        task_store=LocalTaskStore(project / "tasks"),
        artifact_store=LocalArtifactStore(project / "artifacts"),
        run_store=LocalRunStore(project / "runs"),
    )


def test_context_save_regenerates_markdown(tmp_path: Path) -> None:
    project = seed_project(tmp_path)
    service = build_service(project)
    context, _ = service.get_context()
    context = context.model_copy(update={"active_work": "변경된 작업"})

    _, markdown = service.save_context(context)

    assert "변경된 작업" in markdown
    assert "변경된 작업" in (project / "03_context.md").read_text(encoding="utf-8")


def test_end_to_end_pm_and_critic_flow(tmp_path: Path) -> None:
    project = seed_project(tmp_path)
    service = build_service(project)
    detail = service.create_requirements_task()

    detail = service.dispatch_pm(detail.task.id)
    assert detail.task.status.value == "in_progress"
    assert detail.pm_packet is not None

    pm_output = """# 요구사항 정의서 초안

## 배경
프로젝트 배경

## 목표
PoC 범위를 정의한다.

## 기능 요구사항
- 사내 문서 기반 Q&A

## 비기능 요구사항
- 응답 속도 5초 이내

## 오픈 이슈
- 고객 내부 정책 확인 필요

## 다음 액션
- 이해관계자 리뷰
"""
    detail = service.ingest_pm(detail.task.id, pm_output)
    assert len(detail.artifacts) == 1

    detail = service.dispatch_critic(detail.task.id)
    assert detail.critic_packet is not None

    critic_review = """---
verdict: approve
summary: 데모용 요구사항 정의서로 충분히 명확합니다.
missing_items:
  - 고객 승인 일정 확인
recommended_changes:
  - 성공 지표를 한 줄 추가
---
전반적으로 발표용 시연에 적합합니다.
"""
    detail = service.ingest_critic(detail.task.id, critic_review)
    assert detail.task.status.value == "review_requested"
    assert len(detail.artifacts) == 2