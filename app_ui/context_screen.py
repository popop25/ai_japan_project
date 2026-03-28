from __future__ import annotations

from datetime import date

import streamlit as st

from ai_japan_project.models import Constraints, DecisionEntry, ProjectContext, References
from ai_japan_project.service import ProjectService

from app_ui.screen_utils import parse_multiline
from app_ui.ui_theme import (
    render_highlight_card,
    render_page_header,
    render_section_header,
    status_badge_html,
)


def render_context_editor(service: ProjectService) -> None:
    context, markdown = service.get_context()
    render_page_header(
        "Context Editor",
        "AI가 이어받을 프로젝트 맥락을 정리합니다.",
        "비개발자도 폼만 수정하면 에이전트가 읽을 Context Brief가 자동으로 다시 생성됩니다.",
        badge=status_badge_html("pending"),
    )
    render_section_header(
        "프로젝트 기본 정보",
        "목적, 현재 단계, 제약사항을 먼저 명확히 해두면 뒤쪽 흐름이 훨씬 자연스러워집니다.",
        eyebrow="Edit Context",
    )

    form_col, preview_col = st.columns([1.2, 0.8], gap="large")
    with form_col:
        with st.form("context_form"):
            top_left, top_right = st.columns(2, gap="large")
            with top_left:
                name = st.text_input("프로젝트 이름", value=context.name)
                customer = st.text_input("고객/대상", value=context.customer)
                current_stage = st.text_input("현재 단계", value=context.current_stage)
                last_updated = st.date_input("마지막 업데이트", value=date.fromisoformat(context.last_updated)).isoformat()
            with top_right:
                purpose = st.text_area("프로젝트 목적", value=context.purpose, height=150)
                active_work = st.text_area("진행 중인 작업", value=context.active_work, height=150)

            st.markdown("### 제약사항")
            constraint_columns = st.columns(3, gap="large")
            with constraint_columns[0]:
                technical = st.text_area("기술 제약", value=context.constraints.technical, height=130)
            with constraint_columns[1]:
                schedule = st.text_area("일정 제약", value=context.constraints.schedule, height=130)
            with constraint_columns[2]:
                other = st.text_area("기타 제약", value=context.constraints.other, height=130)

            next_actions_text = st.text_area("다음 액션", value="\n".join(context.next_actions), height=130, help="한 줄에 하나씩 입력하면 됩니다.")
            decisions_text = st.text_area(
                "의사결정 로그",
                value="\n".join(f"{item.date} | {item.decision} | {item.reason}" for item in context.decisions),
                height=150,
                help="형식: 날짜 | 결정 | 이유",
            )
            submitted = st.form_submit_button("Context 저장", use_container_width=True)

        if submitted:
            decisions = []
            for line in decisions_text.splitlines():
                if not line.strip():
                    continue
                parts = [part.strip() for part in line.split("|")]
                if len(parts) != 3:
                    st.error("의사결정 로그는 `날짜 | 결정 | 이유` 형식으로 입력해주세요.")
                    st.stop()
                decisions.append(DecisionEntry(date=parts[0], decision=parts[1], reason=parts[2]))
            updated_context = ProjectContext(
                name=name,
                purpose=purpose,
                customer=customer,
                current_stage=current_stage,
                active_work=active_work,
                last_updated=last_updated,
                constraints=Constraints(technical=technical, schedule=schedule, other=other),
                next_actions=parse_multiline(next_actions_text),
                decisions=decisions,
                references=References(jira=context.references.jira, skills=context.references.skills, notes=context.references.notes),
            )
            service.save_context(updated_context)
            st.session_state["flash_message"] = "프로젝트 맥락과 03_context.md를 갱신했습니다."
            st.session_state["flash_level"] = "success"
            st.rerun()

    with preview_col:
        render_highlight_card(
            "입력 팁",
            "목적은 한 문장으로 또렷하게 적고,\n제약사항은 일정·기술·기타로 나눠 짧게 적는 것이 좋습니다.\n다음 액션은 발표에서 바로 보여줄 수 있는 작업 중심으로 적어두세요.",
        )
        with st.container(border=True):
            st.markdown("### 현재 Context Brief 미리보기")
            st.code(markdown, language="markdown")
        with st.expander("참고 링크 확인", expanded=False):
            st.write(f"Jira: {context.references.jira}")
            st.write(f"Skills: {context.references.skills}")
            st.write(f"Notes: {context.references.notes}")
