from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st

from ai_japan_project.models import Constraints, DecisionEntry, ProjectContext, References, Status
from ai_japan_project.service import ProjectService


st.set_page_config(
    page_title="AI_Japan_project",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

service = ProjectService()


def format_status_label(status: str) -> str:
    labels = {
        "pending": "대기",
        "in_progress": "진행중",
        "revision_needed": "수정 필요",
        "review_requested": "검토 요청",
        "done": "완료",
    }
    return labels.get(status, status)


def show_flash() -> None:
    message = st.session_state.pop("flash_message", None)
    level = st.session_state.pop("flash_level", "success")
    if message:
        getattr(st, level)(message)


def set_flash(message: str, level: str = "success") -> None:
    st.session_state["flash_message"] = message
    st.session_state["flash_level"] = level


def parse_multiline(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def dashboard_tab() -> None:
    dashboard = service.get_dashboard()
    st.subheader("프로젝트 현황")
    top = st.columns(4)
    metrics = [
        ("대기", dashboard.status_counts["pending"]),
        ("진행중", dashboard.status_counts["in_progress"]),
        ("수정 필요", dashboard.status_counts["revision_needed"]),
        ("검토 요청", dashboard.status_counts["review_requested"]),
    ]
    for column, (label, value) in zip(top, metrics):
        column.metric(label, value)

    left, right = st.columns([1.3, 1], gap="large")
    with left:
        st.markdown("### 현재 컨텍스트")
        st.markdown(
            f"""
**목적**  
{dashboard.context.purpose}

**현재 단계**  
{dashboard.context.current_stage}

**현재 작업**  
{dashboard.context.active_work}
            """
        )
        st.markdown("### 활성 Task")
        if dashboard.active_tasks:
            for task in dashboard.active_tasks:
                with st.container(border=True):
                    st.markdown(f"**{task.title}**")
                    st.caption(f"{task.id} · {format_status_label(task.status.value)}")
                    if st.button("작업 공간에서 열기", key=f"open-{task.id}"):
                        st.session_state["selected_task_id"] = task.id
                        st.session_state["active_tab"] = "Task Workspace"
                        st.rerun()
        else:
            st.info("아직 생성된 task가 없습니다.")

    with right:
        st.markdown("### 최근 활동")
        if dashboard.recent_activity:
            for activity in dashboard.recent_activity:
                with st.container(border=True):
                    st.caption(f"{activity.timestamp} · {format_status_label(activity.status.value)}")
                    st.markdown(f"**{activity.task_title}**")
                    st.write(activity.message)
        else:
            st.info("아직 기록된 활동이 없습니다.")

        st.markdown("### 최신 산출물")
        if dashboard.latest_artifacts:
            for artifact in dashboard.latest_artifacts:
                with st.container(border=True):
                    st.markdown(f"**{artifact.title}**")
                    st.caption(f"{artifact.kind} · {artifact.id}")
                    if st.button("산출물 보기", key=f"artifact-{artifact.id}"):
                        st.session_state["selected_artifact_id"] = artifact.id
                        st.session_state["active_tab"] = "Artifact Viewer"
                        st.rerun()
        else:
            st.info("아직 생성된 산출물이 없습니다.")


def context_editor_tab() -> None:
    context, markdown = service.get_context()
    st.subheader("Context Editor")
    st.caption("비개발자도 폼으로 프로젝트 맥락을 수정하면 에이전트용 context brief가 자동으로 갱신됩니다.")

    with st.form("context_form"):
        name = st.text_input("프로젝트 이름", value=context.name)
        purpose = st.text_area("목적", value=context.purpose, height=100)
        customer = st.text_input("고객/대상", value=context.customer)
        current_stage = st.text_input("현재 단계", value=context.current_stage)
        active_work = st.text_area("진행중인 작업", value=context.active_work, height=80)
        last_updated = st.date_input(
            "마지막 업데이트",
            value=date.fromisoformat(context.last_updated),
        ).isoformat()
        technical = st.text_area("기술적 제약", value=context.constraints.technical, height=80)
        schedule = st.text_area("일정 제약", value=context.constraints.schedule, height=80)
        other = st.text_area("기타 제약", value=context.constraints.other, height=80)
        next_actions_text = st.text_area(
            "다음 액션 (한 줄에 하나씩)",
            value="\n".join(context.next_actions),
            height=120,
        )
        decisions_text = st.text_area(
            "의사결정 로그 (`날짜 | 결정 | 이유` 형식, 한 줄에 하나씩)",
            value="\n".join(
                f"{item.date} | {item.decision} | {item.reason}" for item in context.decisions
            ),
            height=140,
        )
        submitted = st.form_submit_button("Context 저장", use_container_width=True)

    if submitted:
        decisions = []
        for line in decisions_text.splitlines():
            if not line.strip():
                continue
            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 3:
                set_flash("의사결정 로그는 `날짜 | 결정 | 이유` 형식이어야 합니다.", "error")
                st.rerun()
            decisions.append(DecisionEntry(date=parts[0], decision=parts[1], reason=parts[2]))
        updated_context = ProjectContext(
            name=name,
            purpose=purpose,
            customer=customer,
            current_stage=current_stage,
            active_work=active_work,
            last_updated=last_updated,
            constraints=Constraints(
                technical=technical,
                schedule=schedule,
                other=other,
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
        set_flash("프로젝트 맥락과 03_context.md가 갱신되었습니다.")
        st.rerun()

    with st.expander("에이전트용 Context Brief 미리보기", expanded=False):
        st.code(markdown, language="markdown")


def task_workspace_tab() -> None:
    st.subheader("Task Workspace")
    st.caption("Context -> Generate -> Review 흐름을 한 화면에서 이어서 진행합니다.")

    create_col, select_col = st.columns([1, 1.2], gap="large")
    with create_col:
        with st.form("create_task_form"):
            title = st.text_input("새 PM task 제목", value="요구사항 정의서 초안 작성")
            create = st.form_submit_button("PM Task 생성", use_container_width=True)
        if create:
            detail = service.create_requirements_task(title)
            st.session_state["selected_task_id"] = detail.task.id
            set_flash("새 PM task가 생성되었습니다.")
            st.rerun()

    tasks = service.list_tasks()
    task_ids = [task.id for task in tasks]
    if not task_ids:
        st.info("먼저 PM task를 생성해 주세요.")
        return

    selected_task_id = st.session_state.get("selected_task_id", task_ids[0])
    if selected_task_id not in task_ids:
        selected_task_id = task_ids[0]
    with select_col:
        selected_task_id = st.selectbox(
            "작업 선택",
            task_ids,
            index=task_ids.index(selected_task_id),
            format_func=lambda task_id: f"{task_id} · {service.get_task_detail(task_id).task.title}",
        )
    st.session_state["selected_task_id"] = selected_task_id
    detail = service.get_task_detail(selected_task_id)
    task = detail.task

    status_steps = [
        ("pending", "1. 대기"),
        ("in_progress", "2. PM 진행"),
        ("review_requested", "3. 사람 검토 요청"),
        ("revision_needed", "3. 수정 필요"),
        ("done", "4. 완료"),
    ]
    st.markdown("### 진행 단계")
    cols = st.columns(len(status_steps))
    for col, (value, label) in zip(cols, status_steps):
        active = task.status.value == value
        prefix = "[x]" if active else "[ ]"
        col.markdown(f"{prefix} {label}")

    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        st.markdown(f"### {task.title}")
        st.caption(f"{task.id} · 상태: {format_status_label(task.status.value)}")
        if task.status in {Status.PENDING, Status.REVISION_NEEDED}:
            if st.button("PM Packet 생성", type="primary", use_container_width=True):
                service.dispatch_pm(task.id)
                set_flash("PM 에이전트용 packet을 생성했습니다.")
                st.rerun()

        if detail.pm_packet:
            with st.expander("PM Packet", expanded=True):
                st.code(detail.pm_packet.content, language="markdown")
                st.caption(f"저장 위치: {detail.pm_packet.path}")

        st.markdown("### PM 결과 업로드")
        with st.form("pm_ingest_form"):
            pm_title = st.text_input("PM 산출물 제목", value="요구사항 정의서 초안")
            pm_content = st.text_area(
                "PM 에이전트 결과 Markdown 붙여넣기",
                height=260,
                placeholder="여기에 Codex/Claude Code가 작성한 요구사항 정의서 초안을 붙여넣으세요.",
            )
            submit_pm = st.form_submit_button("PM 결과 반영", use_container_width=True)
        if submit_pm:
            try:
                service.ingest_pm(task.id, pm_content, pm_title)
                set_flash("PM 산출물을 반영했습니다.")
                st.rerun()
            except ValueError as exc:
                set_flash(str(exc), "error")
                st.rerun()

        if detail.artifacts and any(item.kind == "pm_output" for item in detail.artifacts):
            if st.button("Critic Packet 생성", use_container_width=True):
                try:
                    service.dispatch_critic(task.id)
                    set_flash("Critic review packet을 생성했습니다.")
                    st.rerun()
                except ValueError as exc:
                    set_flash(str(exc), "error")
                    st.rerun()

        if detail.critic_packet:
            with st.expander("Critic Packet", expanded=True):
                st.code(detail.critic_packet.content, language="markdown")
                st.caption(f"저장 위치: {detail.critic_packet.path}")

        st.markdown("### Critic 리뷰 업로드")
        with st.form("critic_ingest_form"):
            critic_content = st.text_area(
                "Critic 리뷰 Markdown 붙여넣기",
                height=220,
                placeholder="YAML front matter가 포함된 Critic 리뷰를 붙여넣으세요.",
            )
            submit_critic = st.form_submit_button("Critic 리뷰 반영", use_container_width=True)
        if submit_critic:
            try:
                service.ingest_critic(task.id, critic_content)
                set_flash("Critic 리뷰를 반영했습니다.")
                st.rerun()
            except ValueError as exc:
                set_flash(str(exc), "error")
                st.rerun()

    with right:
        st.markdown("### 작업 타임라인")
        for event in reversed(task.history):
            with st.container(border=True):
                st.caption(f"{event.timestamp} · {format_status_label(event.status.value)}")
                st.write(event.message)

        st.markdown("### 연결된 산출물")
        if detail.artifacts:
            for artifact in detail.artifacts:
                with st.container(border=True):
                    st.markdown(f"**{artifact.title}**")
                    st.caption(f"{artifact.kind} · {artifact.id}")
                    if st.button("Artifact Viewer에서 열기", key=f"open-artifact-{artifact.id}"):
                        st.session_state["selected_artifact_id"] = artifact.id
                        st.session_state["active_tab"] = "Artifact Viewer"
                        st.rerun()
        else:
            st.info("아직 연결된 산출물이 없습니다.")


def artifact_viewer_tab() -> None:
    st.subheader("Artifact Viewer")
    artifacts = service.artifact_store.list()
    if not artifacts:
        st.info("아직 생성된 산출물이 없습니다.")
        return

    artifact_ids = [artifact.id for artifact in artifacts]
    selected_artifact_id = st.session_state.get("selected_artifact_id", artifact_ids[0])
    if selected_artifact_id not in artifact_ids:
        selected_artifact_id = artifact_ids[0]
    selected_artifact_id = st.selectbox(
        "산출물 선택",
        artifact_ids,
        index=artifact_ids.index(selected_artifact_id),
        format_func=lambda artifact_id: f"{artifact_id} · {(service.get_artifact(artifact_id).title if service.get_artifact(artifact_id) else artifact_id)}",
    )
    st.session_state["selected_artifact_id"] = selected_artifact_id
    artifact = service.get_artifact(selected_artifact_id)
    if artifact is None:
        st.warning("선택한 산출물을 찾을 수 없습니다.")
        return
    st.markdown(f"### {artifact.title}")
    st.caption(f"{artifact.kind} · {artifact.created_at}")
    st.markdown(artifact.content)


st.title("AI_Japan_project")
st.caption("비개발자도 브라우저에서 맥락 입력 -> PM 생성 -> Critic 리뷰 흐름을 수행하는 로컬 데모")
show_flash()

tab_names = ["Dashboard", "Context Editor", "Task Workspace", "Artifact Viewer"]
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

if selected == "Dashboard":
    dashboard_tab()
elif selected == "Context Editor":
    context_editor_tab()
elif selected == "Task Workspace":
    task_workspace_tab()
else:
    artifact_viewer_tab()