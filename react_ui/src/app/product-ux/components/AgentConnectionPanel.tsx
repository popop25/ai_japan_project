import { TaskRecord } from "../types";

interface AgentConnectionPanelProps {
  onContinue: () => void;
  task: TaskRecord;
}

function primaryCtaLabel(task: TaskRecord): string {
  if (task.displayState === "not_started") {
    return "Prepare brief";
  }

  if (task.displayState === "brief_ready") {
    return "Open handoff";
  }

  return task.nextActionLabel;
}

function statusLabel(status: TaskRecord["connectedAgents"][number]["status"]) {
  switch (status) {
    case "connected":
      return "Ready";
    case "reviewing":
      return "Waiting";
    case "waiting":
      return "Standby";
    default:
      return status;
  }
}

export function AgentConnectionPanel({ onContinue, task }: AgentConnectionPanelProps) {
  return (
    <div className="aside-stack">
      <section className="aside-section">
        <div className="aside-label">Connected agents</div>
        <div className="agent-list agent-list--compact">
          {task.connectedAgents.map((agent) => (
            <article key={agent.id} className="agent-item">
              <div className="agent-avatar">{agent.roleLabel.replace(" Agent", "").slice(0, 2).toUpperCase()}</div>
              <div className="agent-info">
                <div className="agent-name">{agent.name}</div>
                <span className="agent-role-badge">Role: {agent.roleLabel.replace(" Agent", "")}</span>
              </div>
              <span className="agent-ready">{statusLabel(agent.status)}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="aside-section">
        <div className="aside-label">Next action</div>
        <div className="next-action-card">
          <div className="na-header">
            <span className="na-eyebrow">Next stage</span>
            <span className="na-step-tag">-&gt; 02 Agent Handoff</span>
          </div>
          <div className="na-body">
            <p className="na-text">{task.nextActionDetail}</p>
            <button className="cta-btn" onClick={onContinue} type="button">
              <span>{primaryCtaLabel(task)}</span>
              <span className="cta-arrow">&gt;</span>
            </button>
          </div>
        </div>
      </section>

      <section className="aside-section">
        <div className="aside-label">Workflow</div>
        <div className="wf-list">
          <div className="wf-row current">
            <span className="wf-num">01</span>
            <span className="wf-name">Task</span>
            <span className="wf-marker">Now</span>
          </div>
          <div className="wf-row">
            <span className="wf-num">02</span>
            <span className="wf-name">Agent Handoff</span>
            <span className="wf-marker">-</span>
          </div>
          <div className="wf-row">
            <span className="wf-num">03</span>
            <span className="wf-name">Review & Share</span>
            <span className="wf-marker">-</span>
          </div>
        </div>
      </section>
    </div>
  );
}
