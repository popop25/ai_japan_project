import { ReactNode } from "react";

import { ProductExperience, ProductViewId, TaskRecord } from "../types";

const VIEWS: Array<{ id: ProductViewId; label: string; helper: string }> = [
  { id: "workboard", label: "Task Inbox / Workboard", helper: "해야 할 일과 결과를 함께 확인" },
  { id: "task", label: "Task Detail", helper: "현재 task와 다음 행동" },
  { id: "handoff", label: "Agent Handoff", helper: "에이전트에 brief 전달" },
  { id: "review", label: "Review Result", helper: "검토 결과와 반영 포인트" },
  { id: "context", label: "Context View", helper: "근거와 결정 맥락" }
];

interface AppShellProps {
  children: ReactNode;
  currentTask: TaskRecord;
  currentView: ProductViewId;
  onSelectTask: (taskId: string) => void;
  onViewChange: (view: ProductViewId) => void;
  product: ProductExperience;
}

export function AppShell({ children, currentTask, currentView, onSelectTask, onViewChange, product }: AppShellProps) {
  const connectedCount = product.agents.filter((agent) => agent.status === "connected").length;

  return (
    <div className="agent-app-shell">
      <aside className="agent-sidebar">
        <div className="agent-brand">
          <span className="agent-brand__eyebrow">AI Japan Project</span>
          <h1>{product.title}</h1>
          <p>{product.subtitle}</p>
        </div>

        <div className="agent-sidebar__block">
          <div className="agent-sidebar__label">Workspace</div>
          <div className="agent-workspace-card">
            <strong>{product.workspaceLabel}</strong>
            <span>{connectedCount} agents connected</span>
            <span>{currentTask.account}</span>
          </div>
        </div>

        <div className="agent-sidebar__block">
          <div className="agent-sidebar__label">Move through the workflow</div>
          <nav className="agent-view-nav">
            {VIEWS.map((view) => (
              <button
                key={view.id}
                className={view.id === currentView ? "agent-view-nav__item is-active" : "agent-view-nav__item"}
                onClick={() => onViewChange(view.id)}
                type="button"
              >
                <span>{view.label}</span>
                <small>{view.helper}</small>
              </button>
            ))}
          </nav>
        </div>

        <div className="agent-sidebar__block">
          <div className="agent-sidebar__label">Task Inbox</div>
          <div className="agent-sidebar__tasks">
            {product.tasks.map((task) => (
              <button
                key={task.id}
                className={task.id === currentTask.id ? "agent-task-chip is-active" : "agent-task-chip"}
                onClick={() => onSelectTask(task.id)}
                type="button"
              >
                <strong>{task.title}</strong>
                <span>{task.nextActionLabel}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="agent-sidebar__block agent-sidebar__note">
          <div className="agent-sidebar__label">Fixture note</div>
          <p>현재 화면은 fixture 기반이며, 연결 상태와 공유 상태는 제품 UX를 보여주기 위한 예시 데이터입니다.</p>
        </div>
      </aside>

      <main className="agent-main">
        <header className="agent-topbar">
          <div>
            <span className="agent-topbar__eyebrow">Connected agent workspace</span>
            <h2>{currentTask.title}</h2>
          </div>
          <div className="agent-topbar__meta">
            <span>{currentTask.stage}</span>
            <span>{currentTask.dueLabel}</span>
            <span>{currentTask.updatedAt}</span>
          </div>
        </header>
        <div className="agent-screen">{children}</div>
      </main>
    </div>
  );
}

