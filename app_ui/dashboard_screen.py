from __future__ import annotations

import streamlit as st

from ai_japan_project.models import Status
from ai_japan_project.service import ProjectService

from app_ui.ui_theme import (
    format_status_label,
    render_bullet_list_card,
    render_empty_state,
    render_highlight_card,
    render_key_value_grid,
    render_metric_cards,
    render_page_header,
    render_section_header,
    status_badge_html,
)


def _dashboard_status(dashboard) -> str:
    for status in ["revision_needed", "review_requested", "in_progress", "pending"]:
        if dashboard.status_counts.get(status, 0):
            return status
    return "done"


def _context_brief(dashboard) -> str:
    lines: list[str] = []
    if dashboard.context.purpose:
        lines.append(f"이번 프로젝트의 목표는 {dashboard.context.purpose}")
    lines.append(f"현재 단계는 {dashboard.context.current_stage}이며, 대상은 {dashboard.context.customer}입니다.")
    lines.append(f"지금은 {dashboard.context.active_work} 중심으로 진행되고 있습니다.")
    lines.append(f"마지막으로 정리된 기준일은 {dashboard.context.last_updated}입니다.")
    return "\n".join(lines)


def _task_guidance(task) -> str:
    if task.status == Status.REVISION_NEEDED:
        return "Critic 피드백을 반영해 초안을 보완할 차례입니다."
    if task.status == Status.REVIEW_REQUESTED:
        return "결과를 확인하고 공유 가능한 상태인지 판단하면 됩니다."
    if task.status == Status.IN_PROGRESS:
        return "외부 에이전트 결과 반영 또는 다음 단계 생성으로 바로 이어갈 수 있습니다."
    if task.status == Status.DONE:
        return "핵심 흐름은 마무리되었습니다. 결과 확인 후 다음 작업으로 넘어갈 수 있습니다."
    return "시작 가능한 작업입니다. PM 프롬프트 생성부터 진행하면 됩니다."


def _task_button_label(task) -> str:
    if task.status == Status.REVISION_NEEDED:
        return "수정 흐름 보기"
    if task.status == Status.REVIEW_REQUESTED:
        return "검토 흐름 보기"
    if task.status == Status.PENDING:
        return "작업 시작하기"
    return "이 작업 이어서 보기"


def _artifact_label(kind: str) -> str:
    return "검토 결과" if kind == "critic_review" else "PM 초안"


def _artifact_summary(kind: str) -> str:
    if kind == "critic_review":
        return "승인 또는 수정 필요 판단과 요약을 바로 확인할 수 있습니다."
    return "이해관계자가 읽을 수 있는 요구사항 초안 문서입니다."


def _primary_action(dashboard) -> dict[str, str | None]:
    context_next = dashboard.context.next_actions[0] if dashboard.context.next_actions else None
    if not dashboard.active_tasks:
        body = "아직 진행 중인 작업은 없습니다. 작업 흐름에서 새 PM 작업을 만들면 안내형 흐름이 바로 시작됩니다."
        if context_next:
            body = f"{body}\n컨텍스트에 적어둔 우선 액션: {context_next}"
        return {
            "title": "첫 작업을 시작할 준비가 되어 있습니다",
            "body": body,
            "button_label": "작업 흐름 열기",
            "target_tab": "작업 흐름",
            "task_id": None,
            "artifact_id": None,
            "status": "pending",
        }

    task = dashboard.active_tasks[0]
    artifact = next((item for item in dashboard.latest_artifacts if item.task_id == task.id), None)

    if task.status == Status.REVISION_NEEDED:
        title = "수정 요청부터 반영하는 것이 우선입니다"
        body = f"{task.title} 작업이 수정 필요 상태입니다. Critic 피드백을 확인하고 보완 포인트를 반영하세요."
        button_label = "수정 필요한 작업 열기"
        target_tab = "작업 흐름"
        artifact_id = None
    elif task.status == Status.REVIEW_REQUESTED and artifact is not None:
        title = "결과를 확인하고 공유할 타이밍입니다"
        body = f"{task.title} 작업이 검토 단계까지 도달했습니다. 최신 산출물을 열어 요약과 결과를 확인한 뒤 공유 준비를 진행하세요."
        button_label = "최신 결과 보기"
        target_tab = "산출물"
        artifact_id = artifact.id
    elif task.status == Status.IN_PROGRESS:
        title = "가장 최근 작업을 이어서 마무리하세요"
        body = f"{task.title} 작업이 진행 중입니다. 외부 에이전트 결과를 반영하거나 다음 단계 프롬프트를 생성하면 흐름이 이어집니다."
        button_label = "현재 작업 이어서 보기"
        target_tab = "작업 흐름"
        artifact_id = None
    elif task.status == Status.DONE and artifact is not None:
        title = "완료된 결과를 확인하고 다음 주제로 넘어갈 수 있습니다"
        body = f"{task.title} 작업은 마무리되었습니다. 최신 산출물과 요약을 확인한 뒤 다음 작업을 준비하세요."
        button_label = "최신 산출물 보기"
        target_tab = "산출물"
        artifact_id = artifact.id
    else:
        title = "시작할 준비가 된 작업이 있습니다"
        body = f"{task.title} 작업이 대기 중입니다. PM 프롬프트를 만들면 초안 작성 흐름이 바로 시작됩니다."
        button_label = "작업 시작하기"
        target_tab = "작업 흐름"
        artifact_id = None

    if context_next:
        body = f"{body}\n컨텍스트에 적어둔 우선 액션: {context_next}"

    return {
        "title": title,
        "body": body,
        "button_label": button_label,
        "target_tab": target_tab,
        "task_id": task.id,
        "artifact_id": artifact_id,
        "status": task.status.value,
    }


def render_dashboard(service: ProjectService) -> None:
    dashboard = service.get_dashboard()
    overall_status = _dashboard_status(dashboard)
    action = _primary_action(dashboard)
    action_status = action["status"] or "pending"
    action_tone = "attention" if action_status == "revision_needed" else "positive" if action_status in {"review_requested", "done"} else "action"

    render_page_header(
        "Control Center",
        "현재 상황과 다음 행동이 바로 읽히는 대시보드",
        "프로젝트 맥락, 우선순위, 최근 신호를 한 화면에 정리해 처음 들어온 사람도 빠르게 이해할 수 있게 만들었습니다.",
        badge=status_badge_html(overall_status),
    )

    brief_col, action_col = st.columns([1.15, 0.85], gap="large")
    with brief_col:
        render_highlight_card(
            "현재 상황 브리핑",
            _context_brief(dashboard),
            badge=status_badge_html(overall_status),
            tone="neutral",
            eyebrow="Current State",
        )
        render_key_value_grid(
            [
                ("고객/대상", dashboard.context.customer),
                ("현재 단계", dashboard.context.current_stage),
                ("진행 중인 작업", dashboard.context.active_work),
                ("최근 업데이트", dashboard.context.last_updated),
            ]
        )
    with action_col:
        render_highlight_card(
            action["title"] or "다음 행동",
            action["body"] or "작업 흐름에서 다음 단계를 이어가세요.",
            badge=status_badge_html(action_status),
            tone=action_tone,
            eyebrow="Next Action",
        )
        if st.button(action["button_label"] or "작업 흐름 열기", type="primary", use_container_width=True):
            if action["task_id"]:
                st.session_state["selected_task_id"] = action["task_id"]
            if action["artifact_id"]:
                st.session_state["selected_artifact_id"] = action["artifact_id"]
            st.session_state["active_tab"] = action["target_tab"] or "작업 흐름"
            st.rerun()

    review_needed = dashboard.status_counts["revision_needed"] + dashboard.status_counts["review_requested"]
    next_action_count = len(dashboard.context.next_actions) if dashboard.context.next_actions else (1 if dashboard.active_tasks else 0)
    render_metric_cards(
        [
            ("지금 진행 중", dashboard.status_counts["in_progress"], "현재 바로 이어서 처리할 수 있는 흐름 수"),
            ("검토/보완 필요", review_needed, "결정이나 수정 반영이 필요한 항목 수"),
            ("다음 액션", next_action_count, "컨텍스트와 최근 작업에서 읽히는 우선순위 수"),
        ]
    )

    focus_col, queue_col = st.columns([0.92, 1.08], gap="large")
    with focus_col:
        render_section_header(
            "이번에 챙길 포인트",
            "설명형으로 읽을 수 있게 다음 액션과 최근 결정을 먼저 모았습니다.",
            eyebrow="Focus Notes",
        )
        render_bullet_list_card(
            "다음 액션 목록",
            dashboard.context.next_actions,
            "컨텍스트에 기록된 다음 액션이 아직 없습니다. 컨텍스트 화면에서 우선순위를 남기면 여기서 바로 보입니다.",
            badge=status_badge_html("in_progress" if dashboard.context.next_actions else "pending"),
            eyebrow="Action Queue",
        )
        if dashboard.context.decisions:
            latest_decision = dashboard.context.decisions[-1]
            render_highlight_card(
                f"최근 결정 · {latest_decision.date}",
                f"{latest_decision.decision}\n{latest_decision.reason}",
                tone="positive",
                eyebrow="Latest Decision",
            )
        else:
            render_empty_state(
                "최근 결정이 아직 없습니다.",
                "컨텍스트 화면에 결정 로그를 남겨두면 대시보드에서 공유 포인트로 함께 보여줍니다.",
            )

    with queue_col:
        render_section_header(
            "최근 작업",
            "현재 흐름을 바로 이어갈 수 있도록 상태와 권장 행동을 함께 보여줍니다.",
            eyebrow="Work Queue",
        )
        if dashboard.active_tasks:
            for task in dashboard.active_tasks:
                with st.container(border=True):
                    head_col, badge_col = st.columns([0.72, 0.28], gap="small")
                    with head_col:
                        st.markdown(f"#### {task.title}")
                        st.caption(f"{format_status_label(task.status.value)} · 마지막 업데이트 {task.updated_at}")
                    with badge_col:
                        st.markdown(status_badge_html(task.status.value), unsafe_allow_html=True)
                    st.write(_task_guidance(task))
                    if st.button(_task_button_label(task), key=f"open-task-{task.id}", use_container_width=True):
                        st.session_state["selected_task_id"] = task.id
                        st.session_state["active_tab"] = "작업 흐름"
                        st.rerun()
        else:
            render_empty_state(
                "아직 생성된 작업이 없습니다.",
                "작업 흐름 화면에서 새 PM 작업을 만들면 이 영역에 진행 상황이 쌓입니다.",
            )

    signal_col, artifact_col = st.columns(2, gap="large")
    with signal_col:
        render_section_header(
            "최근 활동",
            "무슨 일이 있었는지 흐름으로 설명할 수 있도록 최신 이벤트만 추렸습니다.",
            eyebrow="Latest Signals",
        )
        if dashboard.recent_activity:
            for activity in dashboard.recent_activity[:5]:
                with st.container(border=True):
                    head_col, badge_col = st.columns([0.72, 0.28], gap="small")
                    with head_col:
                        st.caption(activity.timestamp)
                        st.markdown(f"**{activity.task_title}**")
                    with badge_col:
                        st.markdown(status_badge_html(activity.status.value), unsafe_allow_html=True)
                    st.write(activity.message)
        else:
            render_empty_state(
                "아직 활동 기록이 없습니다.",
                "첫 작업을 생성하면 이 영역에 최근 흐름이 쌓입니다.",
            )

    with artifact_col:
        render_section_header(
            "최신 산출물",
            "문서와 검토 결과를 최신순으로 확인하고 바로 열 수 있습니다.",
            eyebrow="Artifacts",
        )
        if dashboard.latest_artifacts:
            for artifact in dashboard.latest_artifacts[:4]:
                with st.container(border=True):
                    st.markdown(f"**{artifact.title}**")
                    st.caption(f"{_artifact_label(artifact.kind)} · {artifact.created_at}")
                    st.write(_artifact_summary(artifact.kind))
                    if st.button("산출물 열기", key=f"artifact-{artifact.id}", use_container_width=True):
                        st.session_state["selected_artifact_id"] = artifact.id
                        st.session_state["active_tab"] = "산출물"
                        st.rerun()
        else:
            render_empty_state(
                "아직 산출물이 없습니다.",
                "작업 흐름에서 PM 초안이나 Critic 리뷰를 반영하면 여기에 최신 결과가 보입니다.",
            )
