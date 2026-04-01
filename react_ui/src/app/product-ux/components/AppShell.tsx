import { ReactNode } from "react";
import * as Dialog from "@radix-ui/react-dialog";

import { ProductExperience, ProductViewId, TaskRecord } from "../types";
import { ContextPanel } from "./ContextPanel";
import { WorkboardList } from "./WorkboardList";

const STAGES: Array<{ id: ProductViewId; label: string }> = [
  { id: "task", label: "Task" },
  { id: "handoff", label: "Agent Handoff" },
  { id: "review", label: "Review & Share" },
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
            Task picker
          </button>
          <button className="utility-btn" onClick={() => onContextOpenChange(true)} type="button">
            Context
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
          <span className="eyebrow">Demo scope</span>
          <p>
            This demo stays honest about manual handoff. The workspace prepares the next move, and the user uses their own
            agent to continue the work.
          </p>
        </footer>
      </div>

      <Dialog.Root open={taskPickerOpen} onOpenChange={onTaskPickerOpenChange}>
        <Dialog.Portal>
          <Dialog.Overlay className="drawer-overlay" />
          <Dialog.Content className="drawer drawer--left">
            <div className="drawer__header">
              <div>
                <Dialog.Title>Task picker</Dialog.Title>
                <Dialog.Description>Choose the task you want to continue now.</Dialog.Description>
              </div>
              <Dialog.Close asChild>
                <button className="drawer__close" type="button" aria-label="Close task picker">
                  Close
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
                <Dialog.Title>Task context</Dialog.Title>
                <Dialog.Description>Review the context and source notes behind the current task.</Dialog.Description>
              </div>
              <Dialog.Close asChild>
                <button className="drawer__close" type="button" aria-label="Close context panel">
                  Close
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
