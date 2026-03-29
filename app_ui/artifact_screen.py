from __future__ import annotations

import streamlit as st

from ai_japan_project.service import ProjectService
from ai_japan_project.storage import split_frontmatter

from app_ui.screen_utils import get_artifact_source, summarize_markdown_document, summarize_text
from app_ui.ui_theme import (
    render_empty_state,
    render_highlight_card,
    render_key_value_grid,
    render_page_header,
    render_section_header,
    status_badge_html,
)


def render_outline(summary: dict[str, str | int | list[dict[str, int | str]]]) -> None:
    with st.container(border=True):
        st.markdown("### 먼저 확인할 핵심 항목")
        for section in summary["sections"]:
            st.markdown(f"**{section['title']}**")
            st.caption(str(section["summary"]))


def render_pm_artifact(artifact) -> None:
    summary = summarize_markdown_document(artifact.content)
    render_highlight_card(
        str(summary["title"]),
        str(summary["summary"]),
        badge=status_badge_html("in_progress"),
    )
    render_key_value_grid(
        [
            ("문서 종류", "요구사항 정의서 초안"),
            ("주요 섹션", str(summary["section_count"])),
            ("연결 작업", artifact.task_id),
        ]
    )
    render_outline(summary)
    with st.expander("문서 전체 펼쳐보기", expanded=False):
        st.markdown(artifact.content)


def render_critic_artifact(artifact) -> None:
    raw_text = get_artifact_source(artifact)
    frontmatter, notes = split_frontmatter(raw_text)
    verdict = frontmatter.get("verdict", "revise")
    summary = str(frontmatter.get("summary") or "요약이 제공되지 않았습니다.").strip() or "요약이 제공되지 않았습니다."
    verdict_label = "승인" if verdict == "approve" else "수정 필요"
    badge = status_badge_html("review_requested" if verdict == "approve" else "revision_needed")
    next_action = (
        "최종 공유 전에 PM 초안 원문과 남은 메모를 한 번 더 확인하세요."
        if verdict == "approve"
        else "작업 흐름 화면으로 돌아가 수정 반영용 PM 요청문을 다시 만들면 됩니다."
    )

    render_highlight_card(f"Critic 판단: {verdict_label}", summary, badge=badge)
    render_key_value_grid(
        [
            ("판단", verdict_label),
            ("누락 항목", str(len(frontmatter.get("missing_items") or []))),
            ("수정 권고", str(len(frontmatter.get("recommended_changes") or []))),
        ]
    )
    render_highlight_card("다음으로 확인할 것", summarize_text(next_action, limit=180))

    left, right = st.columns(2, gap="large")
    with left:
        with st.container(border=True):
            st.markdown("### 누락된 항목")
            missing_items = frontmatter.get("missing_items") or []
            if missing_items:
                for item in missing_items:
                    st.markdown(f"- {item}")
            else:
                st.write("명시된 누락 항목은 없습니다.")
    with right:
        with st.container(border=True):
            st.markdown("### 수정 권고")
            recommended_changes = frontmatter.get("recommended_changes") or []
            if recommended_changes:
                for item in recommended_changes:
                    st.markdown(f"- {item}")
            else:
                st.write("명시된 수정 권고는 없습니다.")

    if notes.strip():
        with st.container(border=True):
            st.markdown("### 추가 메모")
            st.markdown(notes)

    with st.expander("원문 리뷰 보기", expanded=False):
        st.code(raw_text, language="markdown")


def render_artifact_viewer(service: ProjectService) -> None:
    artifacts = service.artifact_store.list()
    render_page_header(
        "Artifact Viewer",
        "생성된 문서를 요약부터 차례대로 확인합니다.",
        "핵심 판단과 문서 구조를 먼저 보여주고, 원문 Markdown은 필요할 때 펼쳐볼 수 있게 정리했습니다.",
        badge=status_badge_html("review_requested" if artifacts else "pending"),
    )
    if not artifacts:
        render_empty_state("아직 산출물이 없습니다.", "작업 흐름 화면에서 PM 초안 또는 Critic 리뷰를 먼저 반영해 주세요.")
        return

    artifact_ids = [artifact.id for artifact in artifacts]
    selected_artifact_id = st.session_state.get("selected_artifact_id", artifact_ids[0])
    if selected_artifact_id not in artifact_ids:
        selected_artifact_id = artifact_ids[0]
    selected_artifact_id = st.selectbox(
        "확인할 문서 선택",
        artifact_ids,
        index=artifact_ids.index(selected_artifact_id),
        format_func=lambda artifact_id: f"{service.get_artifact(artifact_id).title} · {artifact_id}",
    )
    st.session_state["selected_artifact_id"] = selected_artifact_id
    artifact = service.get_artifact(selected_artifact_id)
    if artifact is None:
        st.warning("선택한 산출물을 찾을 수 없습니다.")
        return

    render_section_header(artifact.title, "먼저 요약과 핵심 판단을 보고, 필요하면 전체 문서와 원문 Markdown을 확인하세요.", eyebrow="Document Summary")
    render_key_value_grid([("종류", artifact.kind), ("작성 시각", artifact.created_at), ("연결 작업", artifact.task_id)])

    if artifact.kind == "critic_review":
        render_critic_artifact(artifact)
    else:
        render_pm_artifact(artifact)

    with st.expander("기술 정보", expanded=False):
        st.write(f"파일 경로: {artifact.path}")
        st.write(f"산출물 ID: {artifact.id}")
