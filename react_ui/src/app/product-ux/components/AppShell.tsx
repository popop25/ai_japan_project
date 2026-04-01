import { ReactNode } from "react";
import * as Dialog from "@radix-ui/react-dialog";

import { ProductExperience, ProductViewId, TaskRecord } from "../types";
import { ContextPanel } from "./ContextPanel";
import { WorkboardList } from "./WorkboardList";

const STAGES: Array<{ id: ProductViewId; label: string; helper: string }> = [
  { id: "task", label: "Task", helper: "Confirm the task, the agent, and the next move." },
  { id: "handoff", label: "Agent Handoff", helper: "Send the brief and wait for the response." },
  { id: "review", label: "Review & Share", helper: "Review the result and confirm the team share state." },
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

function stageIndex(view: ProductViewId): number {
  return STAGES.findIndex((stage) => stage.id === view);
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
  const leadAgent = currentTask.connectedAgents.find((agent) => agent.roleId === currentTask.activeRole) ?? currentTask.connectedAgents[0];
  const shareSnapshot = currentTask.shareStatuses[0];
  const activeStageIndex = stageIndex(currentView);

  return (
    <div className="app-shell">
      <header className="app-shell__header">
        <div className="app-shell__brand">
          <span className="eyebrow">{product.workspaceLabel}</span>
          <h1>{product.title}</h1>
          <p>{product.workspaceTagline}</p>
        </div>

        <div className="app-shell__controls">
          <button className="button button--secondary" onClick={() => onTaskPickerOpenChange(true)} type="button">
            Task picker
          </button>
          <button className="button button--secondary" onClick={() => onContextOpenChange(true)} type="button">
            Context
          </button>
        </div>
      </header>

      <section className="app-shell__focus panel">
        <div className="app-shell__focus-copy">
          <span className="eyebrow">Current task</span>
          <h2>{currentTask.title}</h2>
          <p>{currentTask.summary}</p>
        </div>

        <div className="app-shell__focus-meta">
          <article className="meta-block">
            <span className="eyebrow">Current stage</span>
            <strong>{currentTask.stageLabel}</strong>
            <p>{currentTask.nextActionDetail}</p>
          </article>
          <article className="meta-block">
            <span className="eyebrow">Connected agent</span>
            <strong>{leadAgent ? `${leadAgent.roleLabel} / ${leadAgent.name}` : "No agent selected"}</strong>
            <p>{leadAgent?.statusNote ?? "Connect an agent for the current role."}</p>
          </article>
          <article className="meta-block meta-block--muted">
            <span className="eyebrow">Shared with team</span>
            <strong>{shareSnapshot?.label ?? "Not staged yet"}</strong>
            <p>{shareSnapshot?.detail ?? "The team-share state will appear once the task moves forward."}</p>
          </article>
        </div>
      </section>

      <section className="stage-strip" aria-label="Workflow stages">
        {STAGES.map((stage, index) => {
          const stateClass =
            index < activeStageIndex ? "stage-chip is-complete" : index === activeStageIndex ? "stage-chip is-current" : "stage-chip";

          return (
            <article key={stage.id} className={stateClass}>
              <span className="stage-chip__index">{index + 1}</span>
              <div>
                <strong>{stage.label}</strong>
                <p>{stage.helper}</p>
              </div>
            </article>
          );
        })}
      </section>

      <main className="stage-canvas">{children}</main>

      <footer className="panel panel--muted demo-note">
        <span className="eyebrow">Demo scope</span>
        <p>
          This demo is fixture-based and honest about manual handoff. The workspace prepares the next move, and the user uses
          their own agent to complete the step.
        </p>
      </footer>

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
