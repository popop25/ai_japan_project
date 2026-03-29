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

from app_ui.ui_theme import inject_theme, render_app_shell
from app_ui.workflow_screens import (
    render_artifact_viewer,
    render_context_editor,
    render_dashboard,
    render_task_workspace,
)


TAB_HINTS = {
    "대시보드": "현재 상황과 다음 행동을 먼저 확인합니다.",
    "컨텍스트": "프로젝트 맥락과 기준 문구를 업데이트합니다.",
    "작업 흐름": "PM 초안부터 Critic 검토까지 실제 흐름을 이어갑니다.",
    "산출물": "최신 문서와 리뷰 결과를 확인합니다.",
}


st.set_page_config(
    page_title="AI Japan Project Console",
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

dashboard = service.get_dashboard()
context = dashboard.context
next_action = context.next_actions[0] if context.next_actions else (
    f"{dashboard.active_tasks[0].title} 이어서 진행" if dashboard.active_tasks else "작업 흐름에서 첫 PM 작업 시작"
)

render_app_shell(
    project_name=context.name,
    mode_label=mode_label,
    customer=context.customer,
    current_stage=context.current_stage,
    active_work=context.active_work,
    last_updated=context.last_updated,
    next_action=next_action,
)

tab_names = ["대시보드", "컨텍스트", "작업 흐름", "산출물"]
active_tab = st.session_state.get("active_tab", tab_names[0])
if active_tab not in tab_names:
    active_tab = tab_names[0]

selected = st.radio(
    "Navigation",
    tab_names,
    horizontal=True,
    index=tab_names.index(active_tab),
    label_visibility="collapsed",
)
st.session_state["active_tab"] = selected
st.markdown(f'<div class="ajp-tab-hint">{TAB_HINTS[selected]}</div>', unsafe_allow_html=True)

if selected == "대시보드":
    render_dashboard(service)
elif selected == "컨텍스트":
    render_context_editor(service)
elif selected == "작업 흐름":
    render_task_workspace(service)
else:
    render_artifact_viewer(service)
