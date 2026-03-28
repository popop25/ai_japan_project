from __future__ import annotations

import streamlit as st

from ai_japan_project.models import Status
from ai_japan_project.service import ProjectService

from app_ui.screen_utils import get_latest_artifact, get_workflow_stage, workflow_steps
from app_ui.ui_theme import (
    format_status_label,
    render_empty_state,
    render_highlight_card,
    render_key_value_grid,
    render_page_header,
    render_section_header,
    render_step_track,
    status_badge_html,
)


def render_pm_prompt_section(detail) -> None:
    if detail.pm_packet:
        render_highlight_card(
            "PM에게 전달할 프롬프트가 준비되었습니다.",
            "코드 블록 우측 상단의 복사 버튼을 눌러 Codex 또는 Claude Code로 전달하세요. 결과는 아래 입력창에 그대로 붙여넣으면 됩니다.",
        )
        with st.expander("PM 프롬프트 보기", expanded=True):
            st.code(detail.pm_packet.content, language="markdown")
        with st.expander("기술 정보", expanded=False):
            st.caption(f"저장 위치: {detail.pm_packet.path}")


def render_critic_prompt_section(detail) -> None:
    if detail.critic_packet:
        render_highlight_card(
            "Critic에게 전달할 프롬프트가 준비되었습니다.",
            "검토용 프롬프트를 복사해 전달한 뒤, 돌아온 리뷰를 아래 입력창에 붙여넣으세요.",
            badge=status_badge_html("review_requested"),
        )
        with st.expander("Critic 프롬프트 보기", expanded=True):
            st.code(detail.critic_packet.content, language="markdown")
        with st.expander("기술 정보", expanded=False):
            st.caption(f"저장 위치: {detail.critic_packet.path}")


def render_task_workspace(service: ProjectService) -> None:
    tasks = service.list_tasks()
    selected_task_id = st.session_state.get("selected_task_id")
    selected_detail = None
    if tasks:
        task_ids = [task.id for task in tasks]
        if selected_task_id not in task_ids:
            selected_task_id = task_ids[0]
            st.session_state["selected_task_id"] = selected_task_id
        selected_detail = service.get_task_detail(selected_task_id)

    render_page_header(
        "Guided Workflow",
        "Context → PM 초안 → Critic 검토 → 결과 확인까지 한 화면에서 이어갑니다.",
        "기술적인 내부 정보는 뒤로 숨기고, 지금 사용자가 해야 할 행동이 무엇인지 중심으로 흐름을 정리했습니다.",
        badge=status_badge_html(selected_detail.task.status.value) if selected_detail else status_badge_html("pending"),
    )
    render_step_track(workflow_steps(selected_detail))

    control_left, control_right = st.columns([0.9, 1.1], gap="large")
    with control_left:
        with st.form("create_task_form"):
            title = st.text_input("새 PM 작업 제목", value="요구사항 정의서 초안 작성")
            create = st.form_submit_button("새 작업 만들기", use_container_width=True)
        if create:
            detail = service.create_requirements_task(title)
            st.session_state["selected_task_id"] = detail.task.id
            st.session_state["flash_message"] = "새 PM 작업을 만들었습니다."
            st.session_state["flash_level"] = "success"
            st.rerun()

    with control_right:
        if tasks:
            task_ids = [task.id for task in tasks]
            current_id = st.session_state.get("selected_task_id", task_ids[0])
            selected_task_id = st.selectbox(
                "진행할 작업 선택",
                task_ids,
                index=task_ids.index(current_id),
                format_func=lambda task_id: f"{service.get_task_detail(task_id).task.title} · {task_id}",
            )
            st.session_state["selected_task_id"] = selected_task_id
            selected_detail = service.get_task_detail(selected_task_id)

    if not tasks or selected_detail is None:
        render_empty_state("아직 시작된 작업이 없습니다.", "먼저 PM 초안 생성을 위한 작업을 하나 만들고, 그다음부터 안내형 흐름을 따라가면 됩니다.")
        return

    task = selected_detail.task
    stage = get_workflow_stage(selected_detail)
    pm_artifact = get_latest_artifact(selected_detail, "pm_output")

    render_section_header(task.title, "현재 작업의 상태와 다음 행동을 아래에 순서대로 정리했습니다.", eyebrow="Task Focus")
    render_key_value_grid(
        [
            ("현재 상태", format_status_label(task.status.value)),
            ("역할", task.role.upper()),
            ("산출물", "요구사항 정의서 초안"),
            ("마지막 갱신", task.updated_at),
        ]
    )

    main_col, side_col = st.columns([1.08, 0.92], gap="large")
    with main_col:
        if stage == "create_pm_prompt":
            render_highlight_card(
                "지금 해야 할 일",
                "먼저 PM에게 전달할 프롬프트를 생성하세요. 이 프롬프트를 외부 AI 에이전트에 전달하면 요구사항 정의서 초안을 받을 수 있습니다.",
                badge=status_badge_html(task.status.value),
            )
            if st.button("PM 프롬프트 만들기", type="primary", use_container_width=True):
                service.dispatch_pm(task.id)
                st.session_state["flash_message"] = "PM 프롬프트를 생성했습니다."
                st.session_state["flash_level"] = "success"
                st.rerun()

        render_pm_prompt_section(selected_detail)
        if stage in {"ingest_pm_result", "create_critic_prompt", "ingest_critic_review", "review_outcome"}:
            with st.form("pm_ingest_form"):
                st.markdown("### PM 결과 붙여넣기")
                pm_title = st.text_input("산출물 제목", value="요구사항 정의서 초안")
                pm_content = st.text_area("PM이 작성한 Markdown 초안", height=280, placeholder="AI가 작성한 요구사항 정의서 초안을 여기에 그대로 붙여넣으세요.")
                submit_pm = st.form_submit_button("PM 산출물 반영", use_container_width=True)
            if submit_pm:
                try:
                    service.ingest_pm(task.id, pm_content, pm_title)
                    st.session_state["flash_message"] = "PM 산출물을 반영했습니다."
                    st.session_state["flash_level"] = "success"
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

        if pm_artifact:
            render_highlight_card("PM 초안이 저장되었습니다.", "이제 Critic 리뷰를 통해 승인 또는 수정 필요 여부를 판단할 수 있습니다.", badge=status_badge_html("in_progress"))
            if stage == "create_critic_prompt":
                if st.button("Critic 프롬프트 만들기", use_container_width=True):
                    try:
                        service.dispatch_critic(task.id)
                        st.session_state["flash_message"] = "Critic 프롬프트를 생성했습니다."
                        st.session_state["flash_level"] = "success"
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))

        render_critic_prompt_section(selected_detail)
        if stage in {"ingest_critic_review", "review_outcome"} and selected_detail.critic_packet:
            with st.form("critic_ingest_form"):
                st.markdown("### Critic 리뷰 붙여넣기")
                st.caption("아래 템플릿 형식을 그대로 유지하면 가장 안정적으로 반영됩니다.")
                st.code(
                    """---
verdict: revise
summary: 전체적으로 무엇이 부족한지 한 줄 요약
missing_items:
  - 빠진 내용 1
recommended_changes:
  - 수정 권고 1
---
추가 메모가 있으면 여기에 작성
""",
                    language="yaml",
                )
                critic_content = st.text_area("Critic 리뷰 Markdown", height=240, placeholder="Critic 결과를 그대로 붙여넣으세요.")
                submit_critic = st.form_submit_button("Critic 리뷰 반영", use_container_width=True)
            if submit_critic:
                try:
                    service.ingest_critic(task.id, critic_content)
                    st.session_state["flash_message"] = "Critic 리뷰를 반영했습니다."
                    st.session_state["flash_level"] = "success"
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

        if stage == "review_outcome" and selected_detail.review:
            verdict_label = "승인" if selected_detail.review.verdict == "approve" else "수정 필요"
            badge = status_badge_html("review_requested" if selected_detail.review.verdict == "approve" else "revision_needed")
            render_highlight_card(f"최종 판단: {verdict_label}", selected_detail.review.summary, badge=badge)
            if selected_detail.review.missing_items:
                with st.container(border=True):
                    st.markdown("### 누락된 항목")
                    for item in selected_detail.review.missing_items:
                        st.markdown(f"- {item}")
            if selected_detail.review.recommended_changes:
                with st.container(border=True):
                    st.markdown("### 수정 권고")
                    for item in selected_detail.review.recommended_changes:
                        st.markdown(f"- {item}")

    with side_col:
        render_section_header("작업 히스토리", "지금까지 누가 무엇을 했는지 자연스럽게 보여주는 타임라인입니다.", eyebrow="Timeline")
        for event in reversed(task.history):
            with st.container(border=True):
                st.caption(event.timestamp)
                st.markdown(status_badge_html(event.status.value), unsafe_allow_html=True)
                st.write(event.message)

        st.markdown("### 연결된 산출물")
        if selected_detail.artifacts:
            for artifact in selected_detail.artifacts:
                with st.container(border=True):
                    st.markdown(f"**{artifact.title}**")
                    st.caption(f"{artifact.kind} · {artifact.created_at}")
                    if st.button("산출물 보기", key=f"open-artifact-{artifact.id}", use_container_width=True):
                        st.session_state["selected_artifact_id"] = artifact.id
                        st.session_state["active_tab"] = "산출물"
                        st.rerun()
        else:
            st.info("연결된 산출물이 아직 없습니다.")

        with st.expander("기술 정보", expanded=False):
            st.write(f"작업 ID: {task.id}")
            st.write(f"최신 실행 ID: {task.latest_run_id}")
            st.write(f"연결된 산출물 수: {len(task.artifact_ids)}")
