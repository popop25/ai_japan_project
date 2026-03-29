from __future__ import annotations

import streamlit as st

from ai_japan_project.service import ProjectService

from app_ui.screen_utils import (
    get_latest_artifact,
    get_workflow_stage,
    inspect_critic_submission,
    inspect_pm_submission,
    summarize_markdown_document,
    workflow_steps,
)
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


CRITIC_TEMPLATE = """---
verdict: revise
summary: 전체적으로 무엇이 부족한지 한 줄 요약
missing_items:
  - 빠진 내용 1
recommended_changes:
  - 수정 권고 1
---
추가 메모가 있으면 여기에 작성
"""


def render_action_checklist(title: str, items: list[str]) -> None:
    with st.container(border=True):
        st.markdown(f"### {title}")
        for index, item in enumerate(items, start=1):
            st.markdown(f"{index}. {item}")


def render_feedback(feedback: dict[str, str | int]) -> None:
    message = str(feedback.get("message", ""))
    state = str(feedback.get("state", "empty"))
    if state == "ready":
        st.success(message)
    elif state == "warning":
        st.warning(message)
    else:
        st.info(message)


def render_pm_prompt_section(detail) -> None:
    if detail.pm_packet is None:
        return
    render_highlight_card(
        "PM에 보낼 요청문이 준비되었습니다.",
        "복사 버튼으로 요청문 전체를 복사해 외부 AI에게 그대로 보내세요."
        " 답변으로 받은 초안은 아래 입력칸에 바로 붙여넣으면 됩니다.",
        badge=status_badge_html("in_progress"),
    )
    with st.expander("PM 요청문 전체 보기", expanded=True):
        st.code(detail.pm_packet.content, language="markdown")
    with st.expander("저장 위치", expanded=False):
        st.caption(f"저장 위치: {detail.pm_packet.path}")


def render_critic_prompt_section(detail) -> None:
    if detail.critic_packet is None:
        return
    render_highlight_card(
        "Critic에 보낼 리뷰 요청문이 준비되었습니다.",
        "요청문 전체를 복사해 Critic에게 보내고, 돌아온 리뷰는 아래 입력칸에 그대로 붙여넣으세요.",
        badge=status_badge_html("review_requested"),
    )
    with st.expander("Critic 요청문 전체 보기", expanded=True):
        st.code(detail.critic_packet.content, language="markdown")
    with st.expander("저장 위치", expanded=False):
        st.caption(f"저장 위치: {detail.critic_packet.path}")


def render_pm_snapshot(pm_artifact) -> None:
    summary = summarize_markdown_document(pm_artifact.content)
    render_highlight_card(
        "현재 저장된 PM 초안",
        str(summary["summary"]),
        badge=status_badge_html("in_progress"),
    )
    render_key_value_grid(
        [
            ("문서 제목", pm_artifact.title),
            ("주요 섹션", str(summary["section_count"])),
            ("문서 성격", "이해관계자 검토용 요구사항 초안"),
        ]
    )
    with st.container(border=True):
        st.markdown("### 문서 한눈에 보기")
        for section in summary["sections"]:
            st.markdown(f"**{section['title']}**")
            st.caption(str(section["summary"]))


def render_review_summary(detail) -> None:
    if detail.review is None:
        return
    verdict_label = "승인" if detail.review.verdict == "approve" else "수정 필요"
    badge = status_badge_html("review_requested" if detail.review.verdict == "approve" else "revision_needed")
    render_highlight_card(
        f"가장 최근 Critic 판단: {verdict_label}",
        detail.review.summary,
        badge=badge,
    )
    render_key_value_grid(
        [
            ("판단", verdict_label),
            ("누락 항목", str(len(detail.review.missing_items))),
            ("수정 권고", str(len(detail.review.recommended_changes))),
        ]
    )
    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            st.markdown("### 누락된 항목")
            if detail.review.missing_items:
                for item in detail.review.missing_items:
                    st.markdown(f"- {item}")
            else:
                st.write("명시된 누락 항목은 없습니다.")
    with right:
        with st.container(border=True):
            st.markdown("### 수정 권고")
            if detail.review.recommended_changes:
                for item in detail.review.recommended_changes:
                    st.markdown(f"- {item}")
            else:
                st.write("명시된 수정 권고는 없습니다.")


def render_pm_ingest_section(service: ProjectService, task) -> None:
    title_key = f"pm_title_input_{task.id}"
    content_key = f"pm_content_input_{task.id}"
    st.session_state.setdefault(title_key, "요구사항 정의서 초안")
    st.session_state.setdefault(content_key, "")

    st.markdown("### PM 결과 붙여넣기")
    st.caption("PM이 돌려준 Markdown 문서를 제목 줄부터 끝까지 그대로 붙여넣어 주세요.")
    render_action_checklist(
        "붙여넣기 전에 확인할 것",
        [
            "PM 답변 전체를 복사합니다.",
            "앱 안내문이나 프롬프트 설명은 빼고 문서 본문만 넣습니다.",
            "첫 줄이 문서 제목(`# ...`)인지 한 번 확인합니다.",
        ],
    )
    st.text_input(
        "문서 제목",
        key=title_key,
        help="산출물 목록에 표시될 이름입니다. 그대로 두어도 됩니다.",
    )
    st.text_area(
        "PM이 작성한 Markdown 전체",
        key=content_key,
        height=320,
        placeholder="# 요구사항 정의서 초안\n\n## 배경\n프로젝트 배경...\n\n## 목표\n이번 문서에서 합의할 목표...",
    )
    feedback = inspect_pm_submission(st.session_state[content_key])
    render_feedback(feedback)

    if st.button("PM 초안 반영하기", type="primary", use_container_width=True, disabled=not st.session_state[content_key].strip(), key=f"submit-pm-{task.id}"):
        try:
            service.ingest_pm(task.id, st.session_state[content_key], st.session_state[title_key])
            st.session_state[content_key] = ""
            st.session_state["flash_message"] = "PM 초안을 반영했습니다. 이제 Critic 리뷰 단계로 넘어갈 수 있습니다."
            st.session_state["flash_level"] = "success"
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))


def render_critic_ingest_section(service: ProjectService, task) -> None:
    content_key = f"critic_content_input_{task.id}"
    st.session_state.setdefault(content_key, "")

    st.markdown("### Critic 리뷰 붙여넣기")
    st.caption("Critic 답변 전체를 그대로 붙여넣어 주세요. 맨 위 YAML 블록이 꼭 포함되어야 합니다.")
    render_action_checklist(
        "붙여넣기 전에 확인할 것",
        [
            "리뷰 맨 위의 `---` 블록을 지우지 않습니다.",
            "`verdict` 값이 `approve` 또는 `revise`인지 확인합니다.",
            "추가 메모가 있다면 YAML 아래 본문에 그대로 남겨 둡니다.",
        ],
    )
    with st.expander("형식 예시", expanded=False):
        st.code(CRITIC_TEMPLATE, language="yaml")
    st.text_area(
        "Critic이 작성한 리뷰 전체",
        key=content_key,
        height=280,
        placeholder=CRITIC_TEMPLATE,
    )
    feedback = inspect_critic_submission(st.session_state[content_key])
    render_feedback(feedback)
    if feedback.get("state") != "ready":
        st.caption("버튼은 verdict가 감지되면 활성화됩니다.")

    if st.button(
        "Critic 리뷰 반영하기",
        type="primary",
        use_container_width=True,
        disabled=feedback.get("state") != "ready",
        key=f"submit-critic-{task.id}",
    ):
        try:
            service.ingest_critic(task.id, st.session_state[content_key])
            st.session_state[content_key] = ""
            st.session_state["flash_message"] = "Critic 리뷰를 반영했습니다. 최종 판단을 확인해 주세요."
            st.session_state["flash_level"] = "success"
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))


def render_current_action(stage: str, detail, service: ProjectService) -> None:
    task = detail.task
    if stage == "create_pm_prompt" and detail.review and detail.review.verdict == "revise":
        render_highlight_card(
            "지금 해야 할 일",
            "Critic이 수정이 필요하다고 판단했습니다. 리뷰 내용을 반영할 수 있도록 새 PM 요청문을 다시 만들어 주세요.",
            badge=status_badge_html("revision_needed"),
        )
        render_action_checklist(
            "이번 단계 순서",
            [
                "위의 Critic 판단에서 누락 항목과 수정 권고를 확인합니다.",
                "아래 버튼으로 수정 반영용 PM 요청문을 새로 만듭니다.",
                "PM이 다시 작성한 초안을 다음 단계에서 붙여넣습니다.",
            ],
        )
        if st.button("수정 반영용 PM 요청문 만들기", type="primary", use_container_width=True):
            service.dispatch_pm(task.id)
            st.session_state["flash_message"] = "수정 반영용 PM 요청문을 만들었습니다."
            st.session_state["flash_level"] = "success"
            st.rerun()
        return

    if stage == "create_pm_prompt":
        render_highlight_card(
            "지금 해야 할 일",
            "새 요구사항 초안을 받기 위해 PM 요청문을 먼저 만들어 주세요. 요청문은 Context와 PM 가이드를 합친 문서로 자동 생성됩니다.",
            badge=status_badge_html(task.status.value),
        )
        render_action_checklist(
            "이번 단계 순서",
            [
                "프로젝트 제목과 목적이 맞는지 한 번 확인합니다.",
                "버튼을 눌러 PM 요청문을 만듭니다.",
                "생성된 요청문을 복사해 외부 AI에게 보냅니다.",
            ],
        )
        if st.button("PM 요청문 만들기", type="primary", use_container_width=True):
            service.dispatch_pm(task.id)
            st.session_state["flash_message"] = "PM 요청문을 만들었습니다."
            st.session_state["flash_level"] = "success"
            st.rerun()
        return

    if stage == "ingest_pm_result":
        render_highlight_card(
            "지금 해야 할 일",
            "PM이 돌려준 초안을 아래에 붙여넣어 주세요. 반영이 끝나면 Critic 리뷰 단계가 자동으로 이어집니다.",
            badge=status_badge_html(task.status.value),
        )
        render_action_checklist(
            "이번 단계 순서",
            [
                "위 요청문을 PM에게 보냅니다.",
                "돌아온 Markdown 초안을 전체 복사합니다.",
                "아래 입력칸에 붙여넣고 반영합니다.",
            ],
        )
        render_pm_prompt_section(detail)
        render_pm_ingest_section(service, task)
        return

    if stage == "create_critic_prompt":
        render_highlight_card(
            "지금 해야 할 일",
            "PM 초안이 저장되었습니다. 이제 Critic에게 리뷰를 요청할 차례입니다.",
            badge=status_badge_html("in_progress"),
        )
        render_action_checklist(
            "이번 단계 순서",
            [
                "방금 저장된 PM 초안을 한 번 훑어봅니다.",
                "버튼을 눌러 Critic 요청문을 만듭니다.",
                "요청문을 복사해 Critic에게 보내고 리뷰를 기다립니다.",
            ],
        )
        if st.button("Critic 요청문 만들기", type="primary", use_container_width=True):
            try:
                service.dispatch_critic(task.id)
                st.session_state["flash_message"] = "Critic 요청문을 만들었습니다."
                st.session_state["flash_level"] = "success"
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
        return

    if stage == "ingest_critic_review":
        render_highlight_card(
            "지금 해야 할 일",
            "Critic이 보낸 리뷰를 아래에 붙여넣어 주세요. verdict가 감지되면 반영 버튼이 열립니다.",
            badge=status_badge_html("review_requested"),
        )
        render_action_checklist(
            "이번 단계 순서",
            [
                "위 요청문을 Critic에게 보냅니다.",
                "돌아온 리뷰 전체를 복사합니다.",
                "아래 입력칸에 붙여넣고 결과를 반영합니다.",
            ],
        )
        render_critic_prompt_section(detail)
        render_critic_ingest_section(service, task)
        return

    if detail.review and detail.review.verdict == "approve":
        render_highlight_card(
            "지금 해야 할 일",
            "문서가 승인되었습니다. 아래 판단 요약을 확인한 뒤, 산출물 화면에서 문서 전체를 검토하거나 공유하면 됩니다.",
            badge=status_badge_html("review_requested"),
        )
        render_action_checklist(
            "이번 단계 순서",
            [
                "승인 요약과 남은 보완 메모를 확인합니다.",
                "필요하면 우측 산출물 목록에서 문서를 열어 최종 확인합니다.",
                "다음 작업이 있으면 새 PM 작업을 시작합니다.",
            ],
        )
        return

    render_highlight_card(
        "지금 해야 할 일",
        "수정이 필요한 상태입니다. 위의 Critic 판단을 바탕으로 새 PM 요청문을 다시 만들어 수정 사이클을 시작하세요.",
        badge=status_badge_html("revision_needed"),
    )
    render_action_checklist(
        "이번 단계 순서",
        [
            "누락 항목과 수정 권고를 먼저 읽습니다.",
            "수정 반영용 PM 요청문을 다시 만듭니다.",
            "새 초안을 받아 같은 흐름으로 다시 검토합니다.",
        ],
    )
    if st.button("수정 반영용 PM 요청문 만들기", type="primary", use_container_width=True):
        service.dispatch_pm(task.id)
        st.session_state["flash_message"] = "수정 반영용 PM 요청문을 만들었습니다."
        st.session_state["flash_level"] = "success"
        st.rerun()


def render_task_workspace(service: ProjectService) -> None:
    tasks = service.list_tasks()
    task_details = {task.id: service.get_task_detail(task.id) for task in tasks}
    selected_task_id = st.session_state.get("selected_task_id")
    selected_detail = task_details.get(selected_task_id)
    if tasks and selected_detail is None:
        selected_task_id = tasks[0].id
        st.session_state["selected_task_id"] = selected_task_id
        selected_detail = task_details[selected_task_id]

    render_page_header(
        "Guided Workflow",
        "한 단계씩 요구사항 문서를 완성합니다.",
        "지금 필요한 행동만 먼저 보여주고, 기술 정보는 뒤로 접었습니다.",
        badge=status_badge_html(selected_detail.task.status.value) if selected_detail else status_badge_html("pending"),
    )
    render_step_track(workflow_steps(selected_detail))

    control_left, control_right = st.columns([0.9, 1.1], gap="large")
    with control_left:
        with st.form("create_task_form"):
            title = st.text_input("새 작업 이름", value="요구사항 정의서 초안 작성", help="이번에 만들 문서 주제를 짧게 적어 주세요.")
            create = st.form_submit_button("새 작업 시작", use_container_width=True)
        if create:
            detail = service.create_requirements_task(title)
            st.session_state["selected_task_id"] = detail.task.id
            st.session_state["flash_message"] = "새 작업을 만들었습니다. 바로 PM 요청문 단계로 이어집니다."
            st.session_state["flash_level"] = "success"
            st.rerun()

    with control_right:
        if tasks:
            task_ids = [task.id for task in tasks]
            current_id = st.session_state.get("selected_task_id", task_ids[0])
            selected_task_id = st.selectbox(
                "이어서 진행할 작업",
                task_ids,
                index=task_ids.index(current_id),
                format_func=lambda task_id: f"{task_details[task_id].task.title} · {format_status_label(task_details[task_id].task.status.value)}",
            )
            st.session_state["selected_task_id"] = selected_task_id
            selected_detail = task_details[selected_task_id]

    if not tasks or selected_detail is None:
        render_empty_state(
            "아직 시작된 작업이 없습니다.",
            "새 작업을 하나 만들면 Context 확인부터 PM 초안 생성, Critic 리뷰까지 같은 흐름으로 이어서 진행할 수 있습니다.",
        )
        return

    task = selected_detail.task
    stage = get_workflow_stage(selected_detail)
    pm_artifact = get_latest_artifact(selected_detail, "pm_output")

    render_section_header(task.title, "현재 작업의 상태와 다음 행동을 한 화면에서 이어서 확인할 수 있습니다.", eyebrow="Task Focus")
    render_key_value_grid(
        [
            ("현재 상태", format_status_label(task.status.value)),
            ("현재 단계", workflow_steps(selected_detail)[get_step_index(stage)]["title"]),
            ("산출물", "요구사항 정의서 초안"),
            ("마지막 갱신", task.updated_at),
        ]
    )

    main_col, side_col = st.columns([1.08, 0.92], gap="large")
    with main_col:
        if selected_detail.review and stage == "review_outcome":
            render_review_summary(selected_detail)
        if pm_artifact and stage in {"create_critic_prompt", "ingest_critic_review", "review_outcome"}:
            render_pm_snapshot(pm_artifact)
        render_current_action(stage, selected_detail, service)

    with side_col:
        render_section_header("진행 로그", "지금까지 시스템과 사용자가 무엇을 했는지 시간순으로 확인할 수 있습니다.", eyebrow="Timeline")
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
                    if st.button("열어보기", key=f"open-artifact-{artifact.id}", use_container_width=True):
                        st.session_state["selected_artifact_id"] = artifact.id
                        st.session_state["active_tab"] = "산출물"
                        st.rerun()
        else:
            st.info("아직 저장된 산출물이 없습니다.")

        with st.expander("기술 정보", expanded=False):
            st.write(f"작업 ID: {task.id}")
            st.write(f"최신 실행 ID: {task.latest_run_id}")
            st.write(f"연결된 산출물 수: {len(task.artifact_ids)}")


def get_step_index(stage: str) -> int:
    return {
        "create_task": 0,
        "create_pm_prompt": 1,
        "ingest_pm_result": 1,
        "create_critic_prompt": 2,
        "ingest_critic_review": 2,
        "review_outcome": 3,
    }[stage]



