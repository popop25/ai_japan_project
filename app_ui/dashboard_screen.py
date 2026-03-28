from __future__ import annotations

import streamlit as st

from ai_japan_project.models import Status
from ai_japan_project.service import ProjectService

from app_ui.ui_theme import (
    render_empty_state,
    render_highlight_card,
    render_key_value_grid,
    render_metric_cards,
    render_page_header,
    render_section_header,
    status_badge_html,
)


def render_dashboard(service: ProjectService) -> None:
    dashboard = service.get_dashboard()
    badge = status_badge_html("in_progress" if dashboard.active_tasks else "pending")
    render_page_header(
        "Project Overview",
        "브라우저에서 AI 업무 흐름을 끝까지 추적하세요.",
        "프로젝트 맥락, 진행 상태, 최신 산출물을 한눈에 보여주도록 화면을 정리했습니다.",
        badge=badge,
    )
    render_metric_cards(
        [
            ("준비된 작업", dashboard.status_counts["pending"], "시작 가능한 작업 수"),
            ("진행 중", dashboard.status_counts["in_progress"], "현재 실행 중인 흐름"),
            ("수정 필요", dashboard.status_counts["revision_needed"], "재작업이 필요한 항목"),
            ("리뷰 요청", dashboard.status_counts["review_requested"], "확인 대기 상태"),
        ]
    )

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        render_section_header(
            "현재 프로젝트 상황",
            "발표 전에 지금 어떤 맥락에서 움직이고 있는지 자연스럽게 설명할 수 있도록 정리했습니다.",
            eyebrow="Context Snapshot",
        )
        render_highlight_card("프로젝트 핵심", dashboard.context.purpose, badge=status_badge_html("in_progress"))
        render_key_value_grid(
            [
                ("고객/대상", dashboard.context.customer),
                ("현재 단계", dashboard.context.current_stage),
                ("진행 중인 작업", dashboard.context.active_work),
                ("마지막 업데이트", dashboard.context.last_updated),
            ]
        )

        st.markdown("### 추천 다음 액션")
        if dashboard.active_tasks:
            latest_task = dashboard.active_tasks[0]
            action_text = (
                "작업 흐름 화면으로 이동해 가장 최근 작업을 이어서 진행하세요."
                if latest_task.status != Status.REVIEW_REQUESTED
                else "산출물 화면에서 결과를 확인하고 공유 준비를 진행하세요."
            )
            render_highlight_card(latest_task.title, action_text, badge=status_badge_html(latest_task.status.value))
            if st.button("가장 최근 작업 이어서 보기", use_container_width=True):
                st.session_state["selected_task_id"] = latest_task.id
                st.session_state["active_tab"] = "작업 흐름"
                st.rerun()
        else:
            render_empty_state("아직 작업이 없습니다.", "먼저 작업 흐름 화면에서 PM 작업을 하나 만들어보세요.")

        st.markdown("### 활성 작업")
        if dashboard.active_tasks:
            for task in dashboard.active_tasks:
                with st.container(border=True):
                    st.markdown(f"**{task.title}**")
                    st.markdown(status_badge_html(task.status.value), unsafe_allow_html=True)
                    st.caption(f"작업 ID: {task.id}")
                    if st.button("이 작업 열기", key=f"open-task-{task.id}", use_container_width=True):
                        st.session_state["selected_task_id"] = task.id
                        st.session_state["active_tab"] = "작업 흐름"
                        st.rerun()
        else:
            st.info("표시할 활성 작업이 없습니다.")

    with right:
        render_section_header(
            "최근 활동과 산출물",
            "기술적인 디테일보다는 지금 어디까지 왔는지를 보여주는 타임라인입니다.",
            eyebrow="Latest Activity",
        )
        if dashboard.recent_activity:
            for activity in dashboard.recent_activity[:6]:
                with st.container(border=True):
                    st.caption(activity.timestamp)
                    st.markdown(status_badge_html(activity.status.value), unsafe_allow_html=True)
                    st.markdown(f"**{activity.task_title}**")
                    st.write(activity.message)
        else:
            render_empty_state("아직 활동 기록이 없습니다.", "첫 작업을 생성하면 이 영역에 타임라인이 쌓입니다.")

        st.markdown("### 최신 산출물")
        if dashboard.latest_artifacts:
            for artifact in dashboard.latest_artifacts[:4]:
                with st.container(border=True):
                    st.markdown(f"**{artifact.title}**")
                    st.caption(f"{artifact.kind} · {artifact.created_at}")
                    if st.button("산출물 열기", key=f"artifact-{artifact.id}", use_container_width=True):
                        st.session_state["selected_artifact_id"] = artifact.id
                        st.session_state["active_tab"] = "산출물"
                        st.rerun()
        else:
            st.info("아직 산출물이 없습니다.")
