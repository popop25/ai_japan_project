import { TaskRecord } from "../types";

interface AgentConnectionPanelProps {
  task: TaskRecord;
}

function statusLabel(status: TaskRecord["connectedAgents"][number]["status"]) {
  switch (status) {
    case "connected":
      return "Connected";
    case "reviewing":
      return "Waiting";
    case "waiting":
      return "Standby";
    default:
      return status;
  }
}

export function AgentConnectionPanel({ task }: AgentConnectionPanelProps) {
  return (
    <section className="panel panel--muted">
      <div className="section-heading">
        <span className="eyebrow">Connected agents</span>
        <h3>Who is attached to this workflow</h3>
      </div>

      <div className="agent-list">
        {task.connectedAgents.map((agent) => (
          <article key={agent.id} className="agent-list__item">
            <div>
              <strong>{agent.roleLabel}</strong>
              <p>
                {agent.name} / {agent.productLabel}
              </p>
            </div>
            <div className="agent-list__meta">
              <span className={`state-chip state-chip--${agent.status}`}>{statusLabel(agent.status)}</span>
              <small>{agent.statusNote}</small>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
