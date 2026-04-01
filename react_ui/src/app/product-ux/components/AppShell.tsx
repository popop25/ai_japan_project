import { ReactNode } from "react";
import * as Dialog from "@radix-ui/react-dialog";

import { ProductExperience, ProductViewId, TaskRecord } from "../types";
import { ContextPanel } from "./ContextPanel";
import { WorkboardList } from "./WorkboardList";

const STAGES: Array<{ id: ProductViewId; label: string }> = [
  { id: "task", label: "작업" },
  { id: "handoff", label: "에이전트 전달" },
  { id: "review", label: "검토 및 공유" },
];

interface AppShellProps {
  children: ReactNode;
  currentTask: TaskRecord;
  currentView: ProductViewId;
  onContextOpenChange: (open: boolean) => void;
  onSelectTask: (taskId: string) => void;
  onTaskPickerOpenChange: (open: boolean) => void;
  product: ProductExperience;
  contextOpen: boolean;
  taskPickerOpen: boolean;
}

export function AppShell({
  children,
  currentTask,
  currentView,
  onContextOpenChange,
  onSelectTask,
  onTaskPickerOpenChange,
  product,
  contextOpen,
  taskPickerOpen,
}: AppShellProps) {
  const visibleAgents = currentTask.connectedAgents.filter((agent) => agent.roleId !== "ops").slice(0, 2);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar__brand">
          <span className="logo">{product.title}</span>
          <div className="topbar-sep" />
          <span className="project-crumb">{product.workspaceLabel}</span>
        </div>

        <div className="topbar-right">
          {visibleAgents.map((agent) => (
            <div key={agent.id} className="agent-chip">
              <span className="chip-dot" />
              {agent.name} / {agent.roleLabel.replace(" Agent", "")}
            </div>
          ))}
          <button className="utility-btn" onClick={() => onTaskPickerOpenChange(true)} type="button">
            작업 선택
          </button>
          <button className="utility-btn" onClick={() => onContextOpenChange(true)} type="button">
            맥락
          </button>
        </div>
      </header>

      <nav className="stepnav" aria-label="Workflow stages">
        {STAGES.map((stage, index) => (
          <div className="stepnav__group" key={stage.id}>
            <button className={stage.id === currentView ? "step-btn active" : "step-btn"} type="button">
              <span className="step-num">{String(index + 1).padStart(2, "0")}</span>
              {stage.label}
            </button>
            {index < STAGES.length - 1 ? <span className="step-sep">&gt;</span> : null}
          </div>
        ))}
      </nav>

      <div className="page-wrap">
        <main className="stage-canvas">{children}</main>

        <footer className="demo-note">
          <span className="eyebrow">데모 범위</span>
          <p>
            이 데모는 수동 handoff를 그대로 드러냅니다. 작업 공간은 다음 행동을 정리해주고, 실제 작업은 사용자의 에이전트가 이어서 수행합니다.
          </p>
        </footer>
      </div>

      <Dialog.Root open={taskPickerOpen} onOpenChange={onTaskPickerOpenChange}>
        <Dialog.Portal>
          <Dialog.Overlay className="drawer-overlay" />
          <Dialog.Content className="drawer drawer--left">
            <div className="drawer__header">
              <div>
                <Dialog.Title>작업 선택</Dialog.Title>
                <Dialog.Description>지금 이어서 진행할 작업을 고르세요.</Dialog.Description>
              </div>
              <Dialog.Close asChild>
                <button className="drawer__close" type="button" aria-label="Close task picker">
                  닫기
                </button>
              </Dialog.Close>
            </div>
            <WorkboardList activeTaskId={currentTask.id} onSelectTask={onSelectTask} tasks={product.tasks} />
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>

      <Dialog.Root open={contextOpen} onOpenChange={onContextOpenChange}>
        <Dialog.Portal>
          <Dialog.Overlay className="drawer-overlay" />
          <Dialog.Content className="drawer drawer--right">
            <div className="drawer__header">
              <div>
                <Dialog.Title>작업 맥락</Dialog.Title>
                <Dialog.Description>현재 작업의 배경 맥락과 참고 문서를 확인합니다.</Dialog.Description>
              </div>
              <Dialog.Close asChild>
                <button className="drawer__close" type="button" aria-label="Close context panel">
                  닫기
                </button>
              </Dialog.Close>
            </div>
            <ContextPanel task={currentTask} />
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
