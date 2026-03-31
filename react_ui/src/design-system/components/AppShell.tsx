import { ReactNode } from "react";

import { Connection, ProjectOverview, QueueItem, ViewId, WorkflowWorkspaceData } from "../../types";
import { cx } from "../../utils";
import { Chip } from "./Chip";
import { StatusBadge } from "./StatusBadge";

const NAV_ITEMS: Array<{ id: ViewId; label: string; hint: string }> = [
  { id: "dashboard", label: "Overview", hint: "Current task, stage, action, proof" },
  { id: "workflow", label: "Workflow Detail", hint: "Operate packet, handoff, ingest, review" },
  { id: "artifacts", label: "Artifact Review", hint: "Verdict, summary, source, body" },
  { id: "context", label: "Context", hint: "Canonical brief, decisions, constraints" },
];

interface AppShellProps {
  currentView: ViewId;
  overview: ProjectOverview;
  workflow: WorkflowWorkspaceData;
  queue: QueueItem[];
  connections: Connection[];
  onNavigate: (view: ViewId) => void;
  children: ReactNode;
}

function viewHeading(view: ViewId): { title: string; detail: string } {
  switch (view) {
    case "workflow":
      return {
        title: "Workflow Detail",
        detail: "Run the active task as an explicit state machine with controlled handoff and ingest.",
      };
    case "artifacts":
      return {
        title: "Artifact Review",
        detail: "Lead with verdict, summary, and source links before the document body.",
      };
    case "context":
      return {
        title: "Context",
        detail: "Keep the canonical brief, decisions, and operational guardrails readable together.",
      };
    default:
      return {
        title: "Overview",
        detail: "Read the current situation, make the next decision, and verify traceability in one fold.",
      };
  }
}

export function AppShell({ currentView, overview, workflow, queue, connections, onNavigate, children }: AppShellProps) {
  const heading = viewHeading(currentView);
  const activeTask = queue.find((item) => item.jiraKey === workflow.currentTaskId) ?? queue[0] ?? null;

  return (
    <div className="cp-shell">
      <aside className="cp-rail">
        <div className="cp-rail__brand">
          <div className="cp-rail__mark">AJP</div>
          <div>
            <p className="eyebrow">React Control Plane Spike</p>
            <h1>AI Workflow Operator</h1>
            <p className="muted">
              Fixture-backed product surface. Streamlit remains the live operational shell while this UI sets the next standard.
            </p>
          </div>
        </div>

        <nav className="cp-nav" aria-label="Primary views">
          {NAV_ITEMS.map((item) => (
            <button
              className={cx("cp-nav__item", currentView === item.id && "cp-nav__item--active")}
              key={item.id}
              onClick={() => onNavigate(item.id)}
              type="button"
            >
              <span className="cp-nav__label">{item.label}</span>
              <span className="cp-nav__hint">{item.hint}</span>
            </button>
          ))}
        </nav>

        <section className="cp-rail__section">
          <div className="cp-rail__section-head">
            <span className="eyebrow eyebrow--muted">Operating mode</span>
            <Chip label={overview.modeLabel} tone="brand" />
          </div>
          <p className="muted">{overview.modeDetail}</p>
          <div className="cp-stack cp-stack--tight">
            <div className="meta-row">
              <span>Customer</span>
              <strong>{overview.customer}</strong>
            </div>
            <div className="meta-row">
              <span>Active work</span>
              <strong>{overview.activeWork}</strong>
            </div>
            <div className="meta-row">
              <span>Last updated</span>
              <strong>{overview.lastUpdated}</strong>
            </div>
          </div>
        </section>

        <section className="cp-rail__section">
          <div className="cp-rail__section-head">
            <span className="eyebrow eyebrow--muted">Connected systems</span>
            <span className="cp-rail__count">{connections.length}</span>
          </div>
          <div className="cp-stack cp-stack--tight">
            {connections.map((connection) => (
              <div className="connection-row" key={connection.id}>
                <div>
                  <strong>{connection.name}</strong>
                  <p className="muted">{connection.lastSync}</p>
                </div>
                <StatusBadge status={connection.status} />
              </div>
            ))}
          </div>
        </section>

        {activeTask ? (
          <section className="cp-rail__section cp-rail__section--signal">
            <span className="eyebrow eyebrow--muted">Live focus</span>
            <h2>
              {activeTask.jiraKey} ¡¤ {activeTask.stage}
            </h2>
            <p>{activeTask.nextAction}</p>
          </section>
        ) : null}
      </aside>

      <div className="cp-main">
        <header className="cp-header">
          <div>
            <p className="eyebrow">AI workflow control plane</p>
            <h2>{heading.title}</h2>
            <p className="muted">{heading.detail}</p>
          </div>
          <div className="cp-header__chips">
            <Chip label="Dense" tone="neutral" />
            <Chip label="Operational" tone="warning" />
            <Chip label="Traceable" tone="success" />
          </div>
        </header>

        <main className="cp-page">{children}</main>
      </div>
    </div>
  );
}
