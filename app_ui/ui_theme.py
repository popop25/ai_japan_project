from __future__ import annotations

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
        .stApp {
          background:
            radial-gradient(circle at top left, rgba(49,130,246,.08), transparent 26%),
            linear-gradient(180deg, #f8fbff 0%, #f4f7fb 55%, #eef2f6 100%);
          color: #191f28;
        }
        [data-testid="stHeader"], [data-testid="stToolbar"], footer { visibility: hidden; }
        .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 4rem; }
        .ajp-hero, .ajp-section, .ajp-card, .ajp-metric, .ajp-step {
          background: rgba(255,255,255,.94);
          border: 1px solid #e5e8eb;
          border-radius: 22px;
          box-shadow: 0 16px 36px rgba(15, 23, 42, .06);
        }
        .ajp-hero {
          padding: 2rem;
          margin-bottom: 1rem;
          background: linear-gradient(135deg, rgba(49,130,246,.12), rgba(255,255,255,.97) 42%), #fff;
        }
        .ajp-eyebrow {
          display: inline-block;
          margin-bottom: .5rem;
          color: #1b64da;
          font-size: .84rem;
          font-weight: 700;
          letter-spacing: .04em;
          text-transform: uppercase;
        }
        .ajp-hero h1, .ajp-section h2 { margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -.03em; }
        .ajp-hero p, .ajp-section p, .ajp-card p, .ajp-step p { color: #6b7684; line-height: 1.6; }
        .ajp-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
        .ajp-section, .ajp-card { padding: 1.25rem 1.35rem; margin: .5rem 0 .9rem; }
        .ajp-card h3, .ajp-step h4 { margin: 0; }
        .ajp-metric { padding: 1.1rem 1.2rem; min-height: 126px; }
        .ajp-metric-label { color: #6b7684; font-size: .95rem; font-weight: 600; margin-bottom: .4rem; }
        .ajp-metric-value { font-size: 2rem; font-weight: 800; line-height: 1.05; }
        .ajp-metric-help { color: #6b7684; font-size: .92rem; margin-top: .45rem; }
        .ajp-badge { display: inline-flex; align-items: center; border-radius: 999px; padding: .4rem .8rem; font-size: .84rem; font-weight: 700; white-space: nowrap; }
        .ajp-slate { background: #f2f4f8; color: #4e5968; }
        .ajp-blue { background: rgba(49,130,246,.12); color: #1b64da; }
        .ajp-green { background: #edf9f4; color: #0f7e5b; }
        .ajp-amber { background: #fff6e8; color: #8f5a14; }
        .ajp-step { padding: 1rem; min-height: 150px; }
        .ajp-step-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: .8rem; }
        .ajp-step-index { display: inline-flex; align-items: center; justify-content: center; width: 2rem; height: 2rem; border-radius: 999px; background: #edf2ff; color: #1b64da; font-weight: 800; }
        .ajp-step-current { border-color: rgba(49,130,246,.2); }
        .ajp-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: .85rem; margin-top: .75rem; }
        .ajp-grid-item { background: rgba(247,249,252,.95); border: 1px solid #e5e8eb; border-radius: 16px; padding: .85rem .95rem; }
        .ajp-grid-label { color: #6b7684; font-size: .83rem; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; margin-bottom: .35rem; }
        div[data-testid="stForm"] { border: 1px solid #e5e8eb; border-radius: 22px; padding: 1.1rem 1.1rem .55rem; background: rgba(255,255,255,.92); box-shadow: 0 12px 28px rgba(15, 23, 42, .04); }
        div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div { border-radius: 16px; }
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
          min-height: 3rem; border-radius: 16px; border: none; font-weight: 700;
          background: linear-gradient(180deg, #4a9bff, #3182f6); color: white;
          box-shadow: 0 12px 24px rgba(49,130,246,.22);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
    return f'<span class="ajp-badge ajp-{tone}">{format_status_label(status)}</span>'


def render_page_header(eyebrow: str, title: str, description: str, badge: str | None = None) -> None:
    badge_html = f"<div>{badge}</div>" if badge else ""
    st.markdown(
        f"""
        <section class="ajp-hero">
          <span class="ajp-eyebrow">{eyebrow}</span>
          <div class="ajp-row">
            <div>
              <h1>{title}</h1>
              <p>{description}</p>
            </div>
            {badge_html}
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, description: str, eyebrow: str | None = None) -> None:
    eyebrow_html = f'<span class="ajp-eyebrow">{eyebrow}</span>' if eyebrow else ""
    st.markdown(
        f"""
        <section class="ajp-section">
          {eyebrow_html}
          <h2>{title}</h2>
          <p>{description}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(metrics: list[tuple[str, str | int, str]]) -> None:
    cols = st.columns(len(metrics))
    for col, (label, value, help_text) in zip(cols, metrics):
        col.markdown(
            f"""
            <section class="ajp-metric">
              <div class="ajp-metric-label">{label}</div>
              <div class="ajp-metric-value">{value}</div>
              <div class="ajp-metric-help">{help_text}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )


def render_highlight_card(title: str, body: str, badge: str | None = None) -> None:
    badge_html = f"<div>{badge}</div>" if badge else ""
    paragraphs = "".join(f"<p>{line}</p>" for line in body.splitlines() if line.strip())
    st.markdown(
        f"""
        <section class="ajp-card">
          <div class="ajp-row">
            <h3>{title}</h3>
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
        blocks.append(f'<div class="ajp-grid-item"><div class="ajp-grid-label">{label}</div><div>{value}</div></div>')
    st.markdown(f'<section class="ajp-grid">{"".join(blocks)}</section>', unsafe_allow_html=True)


def render_empty_state(title: str, body: str) -> None:
    st.markdown(f'<section class="ajp-card"><h3>{title}</h3><p>{body}</p></section>', unsafe_allow_html=True)


def render_step_track(steps: list[dict[str, str]]) -> None:
    cols = st.columns(len(steps))
    for col, step in zip(cols, steps):
        badge = "완료" if step["state"] == "done" else "현재 단계" if step["state"] == "current" else "다음 단계"
        tone = "green" if step["state"] == "done" else "blue" if step["state"] == "current" else "slate"
        current_class = " ajp-step-current" if step["state"] == "current" else ""
        col.markdown(
            f"""
            <section class="ajp-step{current_class}">
              <div class="ajp-step-meta">
                <span class="ajp-step-index">{step['index']}</span>
                <span class="ajp-badge ajp-{tone}">{badge}</span>
              </div>
              <h4>{step['title']}</h4>
              <p>{step['description']}</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
