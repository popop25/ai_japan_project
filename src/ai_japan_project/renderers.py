from __future__ import annotations

from textwrap import dedent

import yaml

from .models import Artifact, ProjectContext, Review, Task


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
            - 진행 중인 작업: {context.active_work}
            - 마지막 업데이트: {context.last_updated}

            ## Constraints
            - 기술 제약: {context.constraints.technical}
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
            프로젝트 맥락을 바탕으로 이해관계자가 바로 읽고 피드백할 수 있는 요구사항 정의서 초안을 작성합니다.

            ## Input References
            - project/03_context.md
            - project/skills/pm.md

            ## Output Contract
            - Markdown 문서로만 응답합니다.
            - 반드시 아래 섹션을 포함합니다.
              - 배경
              - 목표
              - 기능 요구사항
              - 비기능 요구사항
              - 오픈 이슈
              - 다음 액션
            - 맥락에 없는 사실은 추정하지 말고 `확인 필요`라고 표시합니다.

            ## Handoff Instructions
            아래 Context와 Skill 문서를 읽고 결과물을 작성한 뒤 최종 Markdown만 반환합니다.

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
            PM 에이전트가 작성한 요구사항 정의서 초안을 검토하고 승인 또는 수정 필요 여부를 판단합니다.

            ## Output Contract
            - 반드시 YAML front matter를 포함합니다.
            - `verdict`는 `approve` 또는 `revise`만 사용합니다.
            - `summary`, `missing_items`, `recommended_changes`를 모두 포함합니다.

            ## Handoff Instructions
            아래 Context, Critic Skill, PM 산출물을 검토한 뒤 지정한 형식으로만 응답합니다.

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


def render_artifact_page_markdown(artifact: Artifact) -> str:
    if artifact.kind != "critic_review":
        return artifact.content.strip() + "\n"

    frontmatter, notes = _split_markdown_frontmatter(artifact.content)
    if not frontmatter:
        return artifact.content.strip() + "\n"

    missing_items = [str(item).strip() for item in frontmatter.get("missing_items") or [] if str(item).strip()]
    recommended_changes = [
        str(item).strip() for item in frontmatter.get("recommended_changes") or [] if str(item).strip()
    ]
    verdict = str(frontmatter.get("verdict") or "revise").strip()
    summary = str(frontmatter.get("summary") or "요약이 제공되지 않았습니다.").strip()

    lines = [
        "## Verdict",
        f"- 상태: {verdict}",
        f"- 요약: {summary}",
        "",
        "## Missing Items",
    ]
    if missing_items:
        lines.extend(f"- {item}" for item in missing_items)
    else:
        lines.append("- 없음")

    lines.extend(["", "## Recommended Changes"])
    if recommended_changes:
        lines.extend(f"- {item}" for item in recommended_changes)
    else:
        lines.append("- 없음")

    if notes.strip():
        lines.extend(["", "## Notes", notes.strip()])
    return "\n".join(lines).strip() + "\n"


def _split_markdown_frontmatter(document: str) -> tuple[dict, str]:
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
