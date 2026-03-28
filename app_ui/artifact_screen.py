from __future__ import annotations

import streamlit as st

from ai_japan_project.service import ProjectService
from ai_japan_project.storage import split_frontmatter

from app_ui.screen_utils import get_artifact_source
from app_ui.ui_theme import (
    render_empty_state,
    render_highlight_card,
    render_key_value_grid,
    render_page_header,
    render_section_header,
    status_badge_html,
)


def render_artifact_viewer(service: ProjectService) -> None:
    artifacts = service.artifact_store.list()
    render_page_header(
        "Artifact Viewer",
        "생성된 문서와 리뷰 결과를 이해하기 쉬운 형태로 확인합니다.",
        "원문 Markdown은 그대로 보존하되, 먼저 핵심 요약과 상태를 보여주는 방식으로 정리했습니다.",
        badge=status_badge_html("review_requested" if artifacts else "pending"),
    )
    if not artifacts:
        render_empty_state("아직 산출물이 없습니다.", "작업 흐름 화면에서 PM 초안 또는 Critic 리뷰를 먼저 반영하세요.")
        return

    artifact_ids = [artifact.id for artifact in artifacts]
    selected_artifact_id = st.session_state.get("selected_artifact_id", artifact_ids[0])
    if selected_artifact_id not in artifact_ids:
        selected_artifact_id = artifact_ids[0]
    selected_artifact_id = st.selectbox(
        "확인할 산출물 선택",
        artifact_ids,
        index=artifact_ids.index(selected_artifact_id),
        format_func=lambda artifact_id: f"{service.get_artifact(artifact_id).title} · {artifact_id}",
    )
    st.session_state["selected_artifact_id"] = selected_artifact_id
    artifact = service.get_artifact(selected_artifact_id)
    if artifact is None:
        st.warning("선택한 산출물을 찾을 수 없습니다.")
        return

    render_section_header(artifact.title, "먼저 핵심 내용을 요약해서 보여주고, 필요하면 원문과 저장 경로를 함께 확인할 수 있습니다.", eyebrow="Artifact Summary")
    render_key_value_grid([("종류", artifact.kind), ("작성 시각", artifact.created_at), ("연결 작업", artifact.task_id)])

    if artifact.kind == "critic_review":
        raw_text = get_artifact_source(artifact)
        frontmatter, notes = split_frontmatter(raw_text)
        verdict = frontmatter.get("verdict", "revise")
        summary = frontmatter.get("summary", "요약이 제공되지 않았습니다.")
        badge = status_badge_html("review_requested" if verdict == "approve" else "revision_needed")
        render_highlight_card("Critic 판단", summary, badge=badge)
        left, right = st.columns(2, gap="large")
        with left:
            with st.container(border=True):
                st.markdown("### 누락된 항목")
                for item in frontmatter.get("missing_items") or []:
                    st.markdown(f"- {item}")
        with right:
            with st.container(border=True):
                st.markdown("### 수정 권고")
                for item in frontmatter.get("recommended_changes") or []:
                    st.markdown(f"- {item}")
        if notes.strip():
            with st.container(border=True):
                st.markdown("### 추가 메모")
                st.markdown(notes)
    else:
        render_highlight_card("PM 산출물", "이 문서는 이해관계자가 읽고 검토할 수 있는 요구사항 정의서 초안입니다.", badge=status_badge_html("in_progress"))
        with st.container(border=True):
            st.markdown(artifact.content)

    with st.expander("원문 Markdown 보기", expanded=False):
        st.code(get_artifact_source(artifact), language="markdown")
    with st.expander("기술 정보", expanded=False):
        st.write(f"파일 경로: {artifact.path}")
        st.write(f"산출물 ID: {artifact.id}")
