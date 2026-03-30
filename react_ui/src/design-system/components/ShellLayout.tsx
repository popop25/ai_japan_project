import { ReactNode } from "react";

import { Connection, ProjectOverview, ViewId } from "../../types";
import { cx } from "../../utils";
import { Chip } from "./Chip";
import { StatusBadge } from "./StatusBadge";

const NAV_ITEMS: Array<{ id: ViewId; label: string; hint: string }> = [
  { id: "dashboard", label: "Dashboard", hint: "Current situation, next action, connected systems" },
  { id: "context", label: "Context Workspace", hint: "Narrative brief and structured project fields" },
  { id: "workflow", label: "Workflow Workspace", hint: "Guided PM and Critic handoff plus ingest" },
  { id: "artifacts", label: "Artifact Viewer", hint: "Summary-first review for drafts and Critic output" },
];

interface ShellLayoutProps {
  currentView: ViewId;
  overview: ProjectOverview;
  connections: Connection[];
  onNavigate: (view: ViewId) => void;
  children: ReactNode;
}

export function ShellLayout({ currentView, overview, connections, onNavigate, children }: ShellLayoutProps) {
  return (
    <div className="app-frame">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <div className="sidebar__brand-mark">AJP</div>
          <div>
            <p className="eyebrow">React UI Spike</p>
            <h1>Control Plane</h1>
            <p className="sidebar__brand-copy">
              Keep Streamlit as the live shell while defining the next product surface.
            </p>
          </div>
        </div>

        <nav className="nav">
          {NAV_ITEMS.map((item) => (
            <button
              className={cx("nav__button", currentView === item.id && "nav__button--active")}
              key={item.id}
              onClick={() => onNavigate(item.id)}
              type="button"
            >
              <span className="nav__label">{item.label}</span>
              <span className="nav__hint">{item.hint}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar__support">
          <div className="sidebar__card">
            <p className="eyebrow eyebrow--muted">Next operator action</p>
            <h2>{overview.nextActionTitle}</h2>
            <p>{overview.nextActionBody}</p>
            <div className="sidebar__chip-row">
              <Chip label={overview.modeLabel} tone="brand" />
              <Chip label="Streamlit remains live" tone="success" />
            </div>
          </div>

          <div className="sidebar__card">
            <p className="eyebrow eyebrow--muted">Connected surface</p>
            <div className="connection-list">
              {connections.map((connection) => (
                <div className="connection-item" key={connection.id}>
                  <div>
                    <h3>{connection.name}</h3>
                    <p>{connection.description}</p>
                  </div>
                  <div className="connection-item__meta">
                    <StatusBadge status={connection.status} />
                    <span>{connection.lastSync}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </aside>

      <div className="main-shell">
        <header className="hero">
          <div className="hero__copy">
            <p className="eyebrow">AI workflow operations</p>
            <h1>{overview.name}</h1>
            <p className="hero__summary">{overview.purpose}</p>
            <div className="hero__chips">
              <Chip label={overview.modeLabel} tone="brand" />
              <Chip label={overview.modeDetail} tone="neutral" />
              <Chip label="Operator-led" tone="success" />
            </div>
          </div>
          <div className="hero__grid">
            <div className="hero-stat">
              <span>Customer</span>
              <strong>{overview.customer}</strong>
            </div>
            <div className="hero-stat">
              <span>Current stage</span>
              <strong>{overview.currentStage}</strong>
            </div>
            <div className="hero-stat">
              <span>Active work</span>
              <strong>{overview.activeWork}</strong>
            </div>
            <div className="hero-stat">
              <span>Last updated</span>
              <strong>{overview.lastUpdated}</strong>
            </div>
          </div>
        </header>

        <main className="page-shell">{children}</main>
      </div>
    </div>
  );
}
