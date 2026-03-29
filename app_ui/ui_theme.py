from __future__ import annotations

from html import escape
from typing import Sequence

import streamlit as st

STATUS_LABELS = {
    "pending": "대기",
    "in_progress": "진행 중",
    "revision_needed": "수정 필요",
    "review_requested": "리뷰 요청",
    "done": "완료",
}


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
          --ajp-bg-top: #f7fbff;
          --ajp-bg-bottom: #eef4fb;
          --ajp-surface: rgba(255, 255, 255, 0.95);
          --ajp-surface-strong: rgba(255, 255, 255, 0.98);
          --ajp-surface-soft: #f6f9fc;
          --ajp-border: rgba(15, 23, 42, 0.08);
          --ajp-border-strong: rgba(33, 78, 161, 0.15);
          --ajp-text: #191f28;
          --ajp-text-subtle: #5f6b7a;
          --ajp-text-muted: #8b95a1;
          --ajp-primary-strong: #1459c7;
          --ajp-primary-soft: rgba(31, 111, 235, 0.1);
          --ajp-success: #127a54;
          --ajp-success-soft: #ebf8f2;
          --ajp-warning: #9a6116;
          --ajp-warning-soft: #fff6e8;
          --ajp-neutral-soft: #f2f5f8;
          --ajp-shadow-lg: 0 22px 48px rgba(15, 23, 42, 0.08);
          --ajp-shadow-md: 0 14px 28px rgba(15, 23, 42, 0.05);
          --ajp-radius-lg: 22px;
          --ajp-radius-md: 18px;
        }
        html, body, [class*="css"] {
          font-family: "Pretendard Variable", "Pretendard", "Noto Sans KR", "Apple SD Gothic Neo", "Segoe UI", sans-serif;
        }
        .stApp {
          background:
            radial-gradient(circle at top left, rgba(31,111,235,.10), transparent 24%),
            radial-gradient(circle at top right, rgba(15,118,110,.05), transparent 18%),
            linear-gradient(180deg, var(--ajp-bg-top) 0%, var(--ajp-bg-bottom) 100%);
          color: var(--ajp-text);
        }
        [data-testid="stHeader"], [data-testid="stToolbar"], footer { visibility: hidden; }
        .block-container {
          max-width: 1180px;
          padding-top: 1.4rem;
          padding-bottom: 4rem;
        }
        .ajp-shell,
        .ajp-page-header,
        .ajp-section,
        .ajp-card,
        .ajp-metric,
        .ajp-step,
        div[data-testid="stVerticalBlockBorderWrapper"] {
          background: var(--ajp-surface);
          border: 1px solid var(--ajp-border);
          border-radius: var(--ajp-radius-lg);
          box-shadow: var(--ajp-shadow-md);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
          padding: 0.25rem;
          background: var(--ajp-surface-strong);
        }
        .ajp-shell {
          padding: 1.55rem 1.6rem 1.45rem;
          margin-bottom: 0.95rem;
          background:
            linear-gradient(135deg, rgba(31,111,235,.08), rgba(255,255,255,.98) 42%),
            var(--ajp-surface-strong);
          border-color: var(--ajp-border-strong);
          box-shadow: var(--ajp-shadow-lg);
        }
        .ajp-shell-top,
        .ajp-row {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 1rem;
        }
        .ajp-shell-kicker,
        .ajp-eyebrow {
          display: inline-block;
          margin-bottom: 0.55rem;
          color: var(--ajp-primary-strong);
          font-size: 0.81rem;
          font-weight: 800;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }
        .ajp-shell-title {
          margin: 0;
          font-size: 2.05rem;
          font-weight: 800;
          letter-spacing: -0.04em;
          line-height: 1.06;
        }
        .ajp-shell-desc,
        .ajp-page-header p,
        .ajp-section p,
        .ajp-card p,
        .ajp-step p {
          color: var(--ajp-text-subtle);
          line-height: 1.6;
        }
        .ajp-shell-desc {
          margin: 0.55rem 0 0;
          max-width: 780px;
        }
        .ajp-shell-meta {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 0.85rem;
          margin-top: 1.3rem;
        }
        .ajp-shell-meta-card {
          background: var(--ajp-surface-soft);
          border: 1px solid var(--ajp-border);
          border-radius: var(--ajp-radius-md);
          padding: 0.95rem 1rem;
        }
        .ajp-shell-meta-label,
        .ajp-grid-label {
          color: var(--ajp-text-muted);
          font-size: 0.77rem;
          font-weight: 800;
          letter-spacing: 0.06em;
          text-transform: uppercase;
        }
        .ajp-shell-meta-value {
          margin-top: 0.45rem;
          font-size: 1rem;
          font-weight: 700;
          color: var(--ajp-text);
        }
        .ajp-shell-foot {
          margin-top: 0.95rem;
          color: var(--ajp-text-muted);
          font-size: 0.88rem;
        }
        .ajp-page-header,
        .ajp-section,
        .ajp-card {
          padding: 1.2rem 1.35rem;
          margin: 0.5rem 0 0.9rem;
        }
        .ajp-page-header {
          background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(246,250,255,.95));
          border-color: rgba(31, 111, 235, 0.08);
        }
        .ajp-page-header h1,
        .ajp-section h2 {
          margin: 0;
          font-size: 1.85rem;
          font-weight: 800;
          letter-spacing: -0.03em;
        }
        .ajp-card h3,
        .ajp-step h4 {
          margin: 0;
          color: var(--ajp-text);
        }
        .ajp-card-head {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 0.9rem;
          margin-bottom: 0.7rem;
        }
        .ajp-card-eyebrow {
          display: block;
          margin-bottom: 0.3rem;
          color: var(--ajp-text-muted);
          font-size: 0.77rem;
          font-weight: 800;
          letter-spacing: 0.05em;
          text-transform: uppercase;
        }
        .ajp-card-action {
          border-color: rgba(31, 111, 235, 0.18);
          background: linear-gradient(180deg, rgba(31,111,235,.06), rgba(255,255,255,.97));
        }
        .ajp-card-positive {
          border-color: rgba(18, 122, 84, 0.18);
          background: linear-gradient(180deg, rgba(18,122,84,.05), rgba(255,255,255,.97));
        }
        .ajp-card-attention {
          border-color: rgba(154, 97, 22, 0.18);
          background: linear-gradient(180deg, rgba(154,97,22,.05), rgba(255,255,255,.97));
        }
        .ajp-card-neutral {
          background: linear-gradient(180deg, rgba(242,245,248,.7), rgba(255,255,255,.97));
        }
        .ajp-metric {
          padding: 1.05rem 1.1rem;
          min-height: 126px;
        }
        .ajp-metric-label {
          color: var(--ajp-text-subtle);
          font-size: 0.92rem;
          font-weight: 700;
          margin-bottom: 0.4rem;
        }
        .ajp-metric-value {
          font-size: 2rem;
          font-weight: 800;
          line-height: 1.05;
          color: var(--ajp-text);
        }
        .ajp-metric-help {
          color: var(--ajp-text-muted);
          font-size: 0.9rem;
          margin-top: 0.5rem;
          line-height: 1.5;
        }
        .ajp-badge-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.45rem;
          justify-content: flex-end;
        }
        .ajp-badge {
          display: inline-flex;
          align-items: center;
          gap: 0.3rem;
          border-radius: 999px;
          padding: 0.4rem 0.82rem;
          font-size: 0.82rem;
          font-weight: 800;
          line-height: 1;
          white-space: nowrap;
        }
        .ajp-slate { background: var(--ajp-neutral-soft); color: #4e5968; }
        .ajp-blue { background: var(--ajp-primary-soft); color: var(--ajp-primary-strong); }
        .ajp-green { background: var(--ajp-success-soft); color: var(--ajp-success); }
        .ajp-amber { background: var(--ajp-warning-soft); color: var(--ajp-warning); }
        .ajp-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 0.85rem;
          margin-top: 0.75rem;
        }
        .ajp-grid-item {
          background: var(--ajp-surface-soft);
          border: 1px solid var(--ajp-border);
          border-radius: 16px;
          padding: 0.85rem 0.95rem;
        }
        .ajp-grid-value {
          margin-top: 0.35rem;
          color: var(--ajp-text);
          font-size: 0.97rem;
          font-weight: 600;
          line-height: 1.5;
        }
        .ajp-list {
          margin: 0;
          padding-left: 1.1rem;
          color: var(--ajp-text-subtle);
        }
        .ajp-list li {
          margin: 0.45rem 0;
          line-height: 1.55;
        }
        .ajp-step {
          padding: 1rem;
          min-height: 150px;
        }
        .ajp-step-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.8rem;
        }
        .ajp-step-index {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 2rem;
          height: 2rem;
          border-radius: 999px;
          background: rgba(31, 111, 235, 0.1);
          color: var(--ajp-primary-strong);
          font-weight: 800;
        }
        .ajp-step-current {
          border-color: rgba(31, 111, 235, 0.22);
          box-shadow: 0 18px 34px rgba(31, 111, 235, 0.08);
        }
        div[data-testid="stForm"] {
          border: 1px solid var(--ajp-border);
          border-radius: var(--ajp-radius-lg);
          padding: 1.1rem 1.1rem 0.55rem;
          background: var(--ajp-surface);
          box-shadow: var(--ajp-shadow-md);
        }
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        div[data-baseweb="select"] > div {
          border-radius: 16px;
          border-color: rgba(15, 23, 42, 0.12);
          background: rgba(255, 255, 255, 0.96);
        }
        div[data-baseweb="input"] input,
        div[data-baseweb="textarea"] textarea {
          color: var(--ajp-text);
        }
        div.stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
          min-height: 3rem;
          border-radius: 16px;
          border: none;
          font-weight: 800;
          background: linear-gradient(180deg, #2f80f7, #1f6feb);
          color: white;
          box-shadow: 0 14px 28px rgba(31, 111, 235, 0.22);
        }
        div.stButton > button[kind="secondary"] {
          background: linear-gradient(180deg, #f5f8fc, #eef3f9);
          color: var(--ajp-text);
          border: 1px solid rgba(15, 23, 42, 0.08);
          box-shadow: none;
        }
        div[data-testid="stAlert"] {
          border-radius: 18px;
          border: 1px solid var(--ajp-border);
        }
        div[data-testid="stExpander"] {
          border: 1px solid var(--ajp-border);
          border-radius: 18px;
          background: rgba(255, 255, 255, 0.86);
        }
        div[data-testid="stRadio"] > div {
          background: rgba(255, 255, 255, 0.9);
          border: 1px solid var(--ajp-border);
          border-radius: 22px;
          padding: 0.38rem;
          box-shadow: var(--ajp-shadow-md);
        }
        div[data-testid="stRadio"] [role="radiogroup"] {
          gap: 0.45rem;
        }
        div[data-testid="stRadio"] label {
          background: transparent;
          border-radius: 16px;
          padding: 0.72rem 1rem;
          min-width: 120px;
          justify-content: center;
          transition: background 0.2s ease;
        }
        div[data-testid="stRadio"] label:hover {
          background: rgba(31, 111, 235, 0.06);
        }
        div[data-testid="stRadio"] label:has(input:checked) {
          background: white;
          box-shadow: 0 10px 20px rgba(15, 23, 42, 0.07);
        }
        .ajp-tab-hint {
          margin-top: -0.15rem;
          margin-bottom: 0.9rem;
          color: var(--ajp-text-subtle);
          font-size: 0.92rem;
        }
        @media (max-width: 900px) {
          .ajp-shell-top,
          .ajp-row,
          .ajp-card-head {
            flex-direction: column;
          }
          .ajp-badge-row {
            justify-content: flex-start;
          }
          .ajp-shell-title,
          .ajp-page-header h1,
          .ajp-section h2 {
            font-size: 1.65rem;
          }
          .block-container {
            padding-top: 1rem;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _escape(value: object) -> str:
    return escape("" if value is None else str(value))


def _escape_multiline(value: object) -> str:
    parts = [segment.strip() for segment in str(value).splitlines() if segment.strip()]
    if not parts:
        return _escape(value)
    return "<br>".join(_escape(part) for part in parts)


def _paragraphs(text: str) -> str:
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    return "".join(f"<p>{_escape(line)}</p>" for line in lines)


def format_status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status)


def status_badge_html(status: str) -> str:
    tone = {
        "pending": "slate",
        "in_progress": "blue",
        "revision_needed": "amber",
        "review_requested": "green",
        "done": "green",
    }.get(status, "slate")
    return f'<span class="ajp-badge ajp-{tone}">{_escape(format_status_label(status))}</span>'


def render_app_shell(
    project_name: str,
    mode_label: str,
    customer: str,
    current_stage: str,
    active_work: str,
    last_updated: str,
    next_action: str,
) -> None:
    st.markdown(
        f"""
        <section class="ajp-shell">
          <div class="ajp-shell-top">
            <div>
              <span class="ajp-shell-kicker">AI Japan Project</span>
              <h1 class="ajp-shell-title">{_escape(project_name)}</h1>
              <p class="ajp-shell-desc">{_escape(customer)}을 위한 업무 흐름을 현재 상황과 다음 행동 중심으로 정리한 운영 화면입니다.</p>
            </div>
            <div class="ajp-badge-row">
              <span class="ajp-badge ajp-slate">운영 콘솔</span>
              <span class="ajp-badge ajp-blue">{_escape(mode_label)}</span>
            </div>
          </div>
          <div class="ajp-shell-meta">
            <div class="ajp-shell-meta-card">
              <div class="ajp-shell-meta-label">현재 단계</div>
              <div class="ajp-shell-meta-value">{_escape(current_stage)}</div>
            </div>
            <div class="ajp-shell-meta-card">
              <div class="ajp-shell-meta-label">현재 집중</div>
              <div class="ajp-shell-meta-value">{_escape(active_work)}</div>
            </div>
            <div class="ajp-shell-meta-card">
              <div class="ajp-shell-meta-label">다음 행동</div>
              <div class="ajp-shell-meta-value">{_escape(next_action)}</div>
            </div>
            <div class="ajp-shell-meta-card">
              <div class="ajp-shell-meta-label">대상</div>
              <div class="ajp-shell-meta-value">{_escape(customer)}</div>
            </div>
          </div>
          <div class="ajp-shell-foot">마지막 컨텍스트 업데이트: {_escape(last_updated)}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(eyebrow: str, title: str, description: str, badge: str | None = None) -> None:
    badge_html = f"<div>{badge}</div>" if badge else ""
    st.markdown(
        f"""
        <section class="ajp-page-header">
          <span class="ajp-eyebrow">{_escape(eyebrow)}</span>
          <div class="ajp-row">
            <div>
              <h1>{_escape(title)}</h1>
              <p>{_escape(description)}</p>
            </div>
            {badge_html}
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, description: str, eyebrow: str | None = None) -> None:
    eyebrow_html = f'<span class="ajp-eyebrow">{_escape(eyebrow)}</span>' if eyebrow else ""
    st.markdown(
        f"""
        <section class="ajp-section">
          {eyebrow_html}
          <h2>{_escape(title)}</h2>
          <p>{_escape(description)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(metrics: list[tuple[str, str | int, str]]) -> None:
    if not metrics:
        return
    cols = st.columns(len(metrics), gap="large")
    for col, (label, value, help_text) in zip(cols, metrics):
        col.markdown(
            f"""
            <section class="ajp-metric">
              <div class="ajp-metric-label">{_escape(label)}</div>
              <div class="ajp-metric-value">{_escape(value)}</div>
              <div class="ajp-metric-help">{_escape(help_text)}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )


def render_highlight_card(
    title: str,
    body: str,
    badge: str | None = None,
    tone: str = "default",
    eyebrow: str | None = None,
) -> None:
    badge_html = f"<div>{badge}</div>" if badge else ""
    paragraphs = _paragraphs(body)
    tone_class = {
        "action": " ajp-card-action",
        "positive": " ajp-card-positive",
        "attention": " ajp-card-attention",
        "neutral": " ajp-card-neutral",
    }.get(tone, "")
    eyebrow_html = f'<span class="ajp-card-eyebrow">{_escape(eyebrow)}</span>' if eyebrow else ""
    st.markdown(
        f"""
        <section class="ajp-card{tone_class}">
          <div class="ajp-card-head">
            <div>
              {eyebrow_html}
              <h3>{_escape(title)}</h3>
            </div>
            {badge_html}
          </div>
          {paragraphs}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_key_value_grid(items: list[tuple[str, str]]) -> None:
    blocks = []
    for label, value in items:
        blocks.append(
            f'<div class="ajp-grid-item">'
            f'<div class="ajp-grid-label">{_escape(label)}</div>'
            f'<div class="ajp-grid-value">{_escape_multiline(value)}</div>'
            f"</div>"
        )
    st.markdown(f'<section class="ajp-grid">{"".join(blocks)}</section>', unsafe_allow_html=True)


def render_empty_state(title: str, body: str) -> None:
    st.markdown(
        f'<section class="ajp-card ajp-card-neutral"><h3>{_escape(title)}</h3><p>{_escape(body)}</p></section>',
        unsafe_allow_html=True,
    )


def render_bullet_list_card(
    title: str,
    items: Sequence[str],
    empty_message: str,
    badge: str | None = None,
    eyebrow: str | None = None,
) -> None:
    badge_html = f"<div>{badge}</div>" if badge else ""
    eyebrow_html = f'<span class="ajp-card-eyebrow">{_escape(eyebrow)}</span>' if eyebrow else ""
    list_items = [item.strip() for item in items if str(item).strip()]
    content_html = (
        '<ul class="ajp-list">' + "".join(f"<li>{_escape(item)}</li>" for item in list_items) + "</ul>"
        if list_items
        else f"<p>{_escape(empty_message)}</p>"
    )
    st.markdown(
        f"""
        <section class="ajp-card ajp-card-neutral">
          <div class="ajp-card-head">
            <div>
              {eyebrow_html}
              <h3>{_escape(title)}</h3>
            </div>
            {badge_html}
          </div>
          {content_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_step_track(steps: list[dict[str, str]]) -> None:
    if not steps:
        return
    cols = st.columns(len(steps), gap="large")
    for col, step in zip(cols, steps):
        badge = "완료" if step["state"] == "done" else "현재 단계" if step["state"] == "current" else "다음 단계"
        tone = "green" if step["state"] == "done" else "blue" if step["state"] == "current" else "slate"
        current_class = " ajp-step-current" if step["state"] == "current" else ""
        col.markdown(
            f"""
            <section class="ajp-step{current_class}">
              <div class="ajp-step-meta">
                <span class="ajp-step-index">{_escape(step['index'])}</span>
                <span class="ajp-badge ajp-{tone}">{_escape(badge)}</span>
              </div>
              <h4>{_escape(step['title'])}</h4>
              <p>{_escape(step['description'])}</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
