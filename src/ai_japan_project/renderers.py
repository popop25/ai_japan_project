from __future__ import annotations

from textwrap import dedent

from .models import ProjectContext, Review, Task


def render_context_markdown(context: ProjectContext) -> str:
    next_actions = "\n".join(
        f"{index}. {item}" for index, item in enumerate(context.next_actions, start=1)
    )
    decisions = "\n".join(
        f"- [{entry.date}] {entry.decision} / {entry.reason}"
        for entry in context.decisions
    )
    return (
        dedent(
            f"""\
            # {context.name} Context Brief

            ## Project
            - 이름: {context.name}
            - 목적: {context.purpose}
            - 고객/대상: {context.customer}

            ## Current Status
            - 현재 단계: {context.current_stage}
            - 진행중인 작업: {context.active_work}
            - 마지막 업데이트: {context.last_updated}

            ## Constraints
            - 기술적 제약: {context.constraints.technical}
            - 일정 제약: {context.constraints.schedule}
            - 기타: {context.constraints.other}

            ## Next Actions
            {next_actions}

            ## Decisions Log
            {decisions}

            ## References
            - Jira: {context.references.jira}
            - Skills: {context.references.skills}
            - Notes: {context.references.notes}
            """
        ).strip()
        + "\n"
    )


def render_pm_packet(task: Task, context_markdown: str, pm_skill_markdown: str) -> str:
    return (
        dedent(
            f"""\
            # PM Agent Work Packet

            ## Task
            - Task ID: {task.id}
            - Title: {task.title}
            - Role: {task.role}
            - Deliverable: 요구사항 정의서 초안

            ## Objective
            프로젝트 맥락을 바탕으로 이해관계자가 바로 읽고 피드백할 수 있는 요구사항 정의서 초안을 작성한다.

            ## Input References
            - project/03_context.md
            - project/skills/pm.md

            ## Output Contract
            - Markdown 문서로만 응답한다.
            - 반드시 다음 섹션을 포함한다.
              - 배경
              - 목표
              - 기능 요구사항
              - 비기능 요구사항
              - 오픈 이슈
              - 다음 액션
            - 맥락에 없는 사실은 단정하지 말고 `확인 필요`라고 표기한다.

            ## Handoff Instructions
            아래 Context와 Skill 문서를 읽고 결과물을 작성한 뒤, 최종 Markdown만 반환한다.

            ---

            ## Context
            {context_markdown}

            ---

            ## PM Skill
            {pm_skill_markdown}
            """
        ).strip()
        + "\n"
    )


def render_critic_packet(
    task: Task,
    context_markdown: str,
    critic_skill_markdown: str,
    pm_output_markdown: str,
) -> str:
    return (
        dedent(
            f"""\
            # Critic Agent Work Packet

            ## Task
            - Task ID: {task.id}
            - Title: {task.title}
            - Stage: critic review

            ## Objective
            PM 에이전트가 작성한 요구사항 정의서 초안을 검토하고 승인 또는 수정 필요 여부를 판단한다.

            ## Output Contract
            - 반드시 YAML front matter를 포함한다.
            - `verdict`는 `approve` 또는 `revise`만 사용한다.
            - `summary`, `missing_items`, `recommended_changes`를 모두 포함한다.

            ## Handoff Instructions
            아래 Context, Critic Skill, PM 산출물을 검토한 뒤 지정된 형식으로만 응답한다.

            ---

            ## Context
            {context_markdown}

            ---

            ## Critic Skill
            {critic_skill_markdown}

            ---

            ## PM Output
            {pm_output_markdown}
            """
        ).strip()
        + "\n"
    )


def render_review_document(review: Review, notes: str = "") -> str:
    lines = [
        "---",
        f"verdict: {review.verdict}",
        f"summary: {review.summary}",
        "missing_items:",
    ]
    for item in review.missing_items:
        lines.append(f"  - {item}")
    lines.append("recommended_changes:")
    for item in review.recommended_changes:
        lines.append(f"  - {item}")
    lines.append("---")
    if notes.strip():
        lines.append(notes.strip())
    return "\n".join(lines).strip() + "\n"