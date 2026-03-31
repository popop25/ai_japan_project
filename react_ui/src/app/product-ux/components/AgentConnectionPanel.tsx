import { AgentRecord, TaskRecord } from "../types";

interface AgentConnectionPanelProps {
  agents: AgentRecord[];
  task: TaskRecord;
}

export function AgentConnectionPanel({ agents, task }: AgentConnectionPanelProps) {
  const connectedAgents = agents.filter((agent) => task.agentIds.includes(agent.id));

  return (
    <section className="agent-panel">
      <div className="agent-panel__header">
        <div>
          <span className="agent-kicker">Connected agent</span>
          <h3>이 task에 연결된 역할</h3>
        </div>
      </div>
      <div className="agent-connection-list">
        {connectedAgents.map((agent) => (
          <article key={agent.id} className="agent-connection-card">
            <div className="agent-connection-card__topline">
              <strong>{agent.name}</strong>
              <span className={`agent-status agent-status--${agent.status}`}>{agent.status}</span>
            </div>
            <p>{agent.role}</p>
            <dl>
              <div>
                <dt>Focus</dt>
                <dd>{agent.focus}</dd>
              </div>
              <div>
                <dt>Queue</dt>
                <dd>{agent.queueDepth}</dd>
              </div>
              <div>
                <dt>Latency</dt>
                <dd>{agent.latency}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}

