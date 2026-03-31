import { AgentRecord, TaskRecord } from "../types";

interface TaskHeroProps {
  agents: AgentRecord[];
  onOpenContext?: () => void;
  onOpenHandoff?: () => void;
  task: TaskRecord;
}

export function TaskHero({ agents, onOpenContext, onOpenHandoff, task }: TaskHeroProps) {
  const connectedAgents = agents.filter((agent) => task.agentIds.includes(agent.id));

  return (
    <section className="task-hero">
      <div className="task-hero__summary agent-panel">
        <div className="agent-kicker">Current task</div>
        <div className="task-hero__headline">
          <div>
            <h3>{task.title}</h3>
            <p>{task.objective}</p>
          </div>
          <span className="task-hero__urgency">{task.urgency}</span>
        </div>
        <div className="task-hero__details">
          <div>
            <span className="agent-mini-label">Account</span>
            <strong>{task.account}</strong>
          </div>
          <div>
            <span className="agent-mini-label">Next action</span>
            <strong>{task.nextActionLabel}</strong>
            <p>{task.nextActionDetail}</p>
          </div>
          <div>
            <span className="agent-mini-label">Why now</span>
            <strong>{task.dueLabel}</strong>
            <p>{task.summary}</p>
          </div>
        </div>
        <div className="task-hero__actions">
          {task.actionLabels.map((label, index) => (
            <button
              key={label}
              className={index === 0 ? "agent-button is-primary" : "agent-button"}
              onClick={index === 0 ? onOpenHandoff : index === 3 ? onOpenContext : undefined}
              type="button"
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="task-hero__stack">
        <section className="agent-panel compact-panel">
          <div className="agent-panel__header">
            <div>
              <span className="agent-kicker">Connected agent</span>
              <h3>내 agent 연결 상태</h3>
            </div>
          </div>
          <div className="hero-agent-list">
            {connectedAgents.map((agent) => (
              <div key={agent.id} className="hero-agent-item">
                <div>
                  <strong>{agent.name}</strong>
                  <p>{agent.role}</p>
                </div>
                <span className={`agent-status agent-status--${agent.status}`}>{agent.status}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="agent-panel compact-panel">
          <div className="agent-panel__header">
            <div>
              <span className="agent-kicker">Shared with team</span>
              <h3>Jira / Confluence 반영 상태</h3>
            </div>
          </div>
          <div className="share-state-list">
            {task.shareStatuses.map((status) => (
              <div key={status.system} className={`share-state share-state--${status.tone}`}>
                <div>
                  <strong>{status.system}</strong>
                  <p>{status.label}</p>
                </div>
                <span>{status.detail}</span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </section>
  );
}

