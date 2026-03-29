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


DECISION_PLACEHOLDER = "2026-03-28 | PM 초안을 먼저 만든다 | 비개발자 데모 전에 문서 흐름을 확정해야 해서"
NEXT_ACTIONS_PLACEHOLDER = "PM 요청문 생성\nPM 초안 붙여넣기\nCritic 리뷰 요청"


def render_context_editor(service: ProjectService) -> None:
    context, markdown = service.get_context()
    render_page_header(
        "Context Editor",
        "PM과 Critic이 읽을 작업 맥락을 먼저 정리합니다.",
        "여기서 저장한 내용은 이후 요청문에 자동으로 반영됩니다. 목적과 현재 단계만 또렷하게 적어도 흐름이 훨씬 쉬워집니다.",
        badge=status_badge_html("pending"),
    )
    render_highlight_card(
        "저장 전에 이 세 가지만 확인하세요.",
        "프로젝트 목적은 한 문장으로 또렷하게 적습니다.\n현재 단계는 지금 상태 그대로 적습니다.\n다음 액션은 한 줄에 하나씩, 바로 실행할 일만 적습니다.",
    )
    render_section_header(
        "입력 순서대로 채우면 됩니다.",
        "프로젝트 소개부터 현재 상황, 제약, 다음 액션 순서로 적으면 PM과 Critic이 읽기 쉬운 Context Brief가 만들어집니다.",
        eyebrow="Edit Context",
    )

    form_col, preview_col = st.columns([1.2, 0.8], gap="large")
    with form_col:
        with st.form("context_form"):
            st.markdown("### 1. 프로젝트를 한 줄로 설명하기")
            intro_left, intro_right = st.columns(2, gap="large")
            with intro_left:
                name = st.text_input(
                    "프로젝트 이름",
                    value=context.name,
                    placeholder="예: AI Japan Workflow Pilot",
                    help="산출물과 작업 목록에서 계속 보게 되는 이름입니다.",
                )
                customer = st.text_input(
                    "고객/대상",
                    value=context.customer,
                    placeholder="예: 내부 운영팀, 시연 참가자",
                    help="이 문서를 최종적으로 읽을 사람이나 팀을 적습니다.",
                )
                current_stage = st.text_input(
                    "현재 단계",
                    value=context.current_stage,
                    placeholder="예: PM 초안 생성 전, Critic 리뷰 반영 중",
                    help="지금 어디까지 왔는지 현재형으로 적어 주세요.",
                )
                last_updated = st.date_input("마지막 업데이트", value=date.fromisoformat(context.last_updated)).isoformat()
            with intro_right:
                purpose = st.text_area(
                    "프로젝트 목적",
                    value=context.purpose,
                    height=150,
                    placeholder="예: 비개발자도 따라갈 수 있는 요구사항 작성 흐름을 만든다.",
                    help="왜 이 프로젝트를 하는지 한두 문장으로 적습니다.",
                )
                active_work = st.text_area(
                    "지금 진행 중인 작업",
                    value=context.active_work,
                    height=150,
                    placeholder="예: Context 정리, PM 초안 생성 UX 개선, Critic 리뷰 반영 흐름 점검",
                    help="현재 실제로 진행 중인 일만 적어 주세요.",
                )

            st.markdown("### 2. 꼭 지켜야 할 조건")
            st.caption("제약은 짧고 명확하게 적을수록 이후 요청문에서 덜 흔들립니다.")
            constraint_columns = st.columns(3, gap="large")
            with constraint_columns[0]:
                technical = st.text_area(
                    "기술 제약",
                    value=context.constraints.technical,
                    height=130,
                    placeholder="예: 외부 AI 호출 방식은 유지, local mode 흐름은 깨지지 않음",
                )
            with constraint_columns[1]:
                schedule = st.text_area(
                    "일정 제약",
                    value=context.constraints.schedule,
                    height=130,
                    placeholder="예: 이번 데모 전까지 PM/Critic 흐름 확정",
                )
            with constraint_columns[2]:
                other = st.text_area(
                    "기타 제약",
                    value=context.constraints.other,
                    height=130,
                    placeholder="예: 비개발자도 5분 안에 따라갈 수 있어야 함",
                )

            st.markdown("### 3. 다음 액션과 최근 결정")
            next_actions_text = st.text_area(
                "다음 액션",
                value="\n".join(context.next_actions),
                height=140,
                placeholder=NEXT_ACTIONS_PLACEHOLDER,
                help="한 줄에 하나씩 적어 주세요. 동사로 시작하면 읽기 쉽습니다.",
            )
            decisions_text = st.text_area(
                "최근 결정",
                value="\n".join(f"{item.date} | {item.decision} | {item.reason}" for item in context.decisions),
                height=170,
                placeholder=DECISION_PLACEHOLDER,
                help="형식: 날짜 | 결정 | 이유",
            )
            submitted = st.form_submit_button("Context 저장", use_container_width=True)

        if submitted:
            required_fields = {
                "프로젝트 이름": name,
                "프로젝트 목적": purpose,
                "현재 단계": current_stage,
            }
            missing_fields = [label for label, value in required_fields.items() if not value.strip()]
            if missing_fields:
                st.error(f"다음 항목을 먼저 채워 주세요: {', '.join(missing_fields)}")
                st.stop()

            decisions = []
            for line in decisions_text.splitlines():
                if not line.strip():
                    continue
                parts = [part.strip() for part in line.split("|")]
                if len(parts) != 3:
                    st.error("최근 결정은 `날짜 | 결정 | 이유` 형식으로 입력해 주세요.")
                    st.stop()
                decisions.append(DecisionEntry(date=parts[0], decision=parts[1], reason=parts[2]))

            updated_context = ProjectContext(
                name=name.strip(),
                purpose=purpose.strip(),
                customer=customer.strip(),
                current_stage=current_stage.strip(),
                active_work=active_work.strip(),
                last_updated=last_updated,
                constraints=Constraints(
                    technical=technical.strip(),
                    schedule=schedule.strip(),
                    other=other.strip(),
                ),
                next_actions=parse_multiline(next_actions_text),
                decisions=decisions,
                references=References(
                    jira=context.references.jira,
                    skills=context.references.skills,
                    notes=context.references.notes,
                ),
            )
            service.save_context(updated_context)
            st.session_state["flash_message"] = "프로젝트 맥락과 03_context.md를 갱신했습니다."
            st.session_state["flash_level"] = "success"
            st.rerun()

    with preview_col:
        render_highlight_card(
            "입력 실수 줄이기 체크",
            "목적은 왜 하는지에만 집중합니다.\n현재 단계는 지금 화면 기준으로 적습니다.\n다음 액션은 발표 자료 제목이 아니라 실제 다음 행동을 적습니다.",
        )
        with st.container(border=True):
            st.markdown("### 저장되면 이렇게 전달됩니다")
            st.caption("PM과 Critic 요청문에 함께 들어가는 Context Brief 미리보기입니다.")
            st.code(markdown, language="markdown")
        with st.expander("참고 링크 확인", expanded=False):
            st.write(f"Jira: {context.references.jira}")
            st.write(f"Skills: {context.references.skills}")
            st.write(f"Notes: {context.references.notes}")
