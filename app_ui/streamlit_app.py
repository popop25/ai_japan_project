from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st

from ai_japan_project.factory import build_project_service
from ai_japan_project.settings import AppMode, AppSettings

from app_ui.ui_theme import inject_theme
from app_ui.workflow_screens import (
    render_artifact_viewer,
    render_context_editor,
    render_dashboard,
    render_task_workspace,
)


st.set_page_config(
    page_title="AI Japan Project",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource
def get_settings() -> AppSettings:
    return AppSettings.from_env()


@st.cache_resource
def get_service() -> object:
    return build_project_service(get_settings())


def show_flash() -> None:
    message = st.session_state.pop("flash_message", None)
    level = st.session_state.pop("flash_level", "success")
    if message:
        getattr(st, level)(message)


inject_theme()
show_flash()

settings = get_settings()
mode_label = "Atlassian Cloud" if settings.mode == AppMode.ATLASSIAN else "Local Demo"

try:
    service = get_service()
except ValueError as exc:
    st.error(f"앱 설정을 확인해주세요: {exc}")
    st.caption("AJP_MODE=atlassian 인 경우 필요한 Atlassian 환경 변수를 모두 설정해야 합니다.")
    st.stop()

context, _ = service.get_context()
st.markdown(
    (
        '<div style="display:flex; justify-content:space-between; align-items:center; '
        'margin-bottom:0.75rem; color:#6b7684; font-size:0.95rem;">'
        f"<span>{context.name}</span>"
        f"<span style=\"padding:0.3rem 0.7rem; border-radius:999px; background:#edf2ff; color:#1b64da; font-weight:700; font-size:0.82rem;\">{mode_label}</span>"
        "</div>"
    ),
    unsafe_allow_html=True,
)

tab_names = ["대시보드", "컨텍스트", "작업 흐름", "산출물"]
active_tab = st.session_state.get("active_tab", tab_names[0])
if active_tab not in tab_names:
    active_tab = tab_names[0]
selected = st.radio("Navigation", tab_names, horizontal=True, index=tab_names.index(active_tab), label_visibility="collapsed")
st.session_state["active_tab"] = selected

if selected == "대시보드":
    render_dashboard(service)
elif selected == "컨텍스트":
    render_context_editor(service)
elif selected == "작업 흐름":
    render_task_workspace(service)
else:
    render_artifact_viewer(service)
