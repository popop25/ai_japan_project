import { AgentRecord, TaskRecord } from "../types";

interface HandoffComposerProps {
  agents: AgentRecord[];
  task: TaskRecord;
}

export function HandoffComposer({ agents, task }: HandoffComposerProps) {
  const targetAgent = agents.find((agent) => agent.id === task.handoffTargetId);

  return (
    <section className="agent-panel">
      <div className="agent-panel__header">
        <div>
          <span className="agent-kicker">Agent Handoff</span>
          <h3>{task.handoffTitle}</h3>
        </div>
        <span className="agent-pill">to {targetAgent?.name ?? "agent"}</span>
      </div>

      <div className="handoff-grid">
        <div className="handoff-card handoff-card--primary">
          <span className="agent-mini-label">보낼 brief</span>
          <p>{task.handoffInstruction}</p>
        </div>
        <div className="handoff-card">
          <span className="agent-mini-label">포함될 맥락</span>
          <ul>
            {task.contextEntries.map((entry) => (
              <li key={entry.id}>
                <strong>{entry.label}</strong>
                <span>{entry.value}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="handoff-actions">
        <button className="agent-button is-primary" type="button">
          {task.nextActionLabel}
        </button>
        <button className="agent-button" type="button">
          초안 받기
        </button>
        <button className="agent-button" type="button">
          Critic에 검토 요청
        </button>
      </div>
    </section>
  );
}

