import { TaskRecord } from "../types";

interface TaskHeroProps {
  onContinue: () => void;
  onOpenContext: () => void;
  task: TaskRecord;
}

export function TaskHero({ onContinue, onOpenContext, task }: TaskHeroProps) {
  const leadAgent = task.connectedAgents.find((agent) => agent.roleId === task.activeRole) ?? task.connectedAgents[0];
  const shareSnapshot = task.shareStatuses[0];

  return (
    <section className="task-layout">
      <article className="panel task-document">
        <div className="section-heading section-heading--row">
          <div>
            <span className="eyebrow">Task</span>
            <h2>{task.title}</h2>
          </div>
          <span className="state-chip state-chip--attention">{task.urgency}</span>
        </div>

        <p className="task-document__summary">{task.objective}</p>

        <div className="task-document__grid">
          <div className="task-document__narrative">
            <div className="note-block">
              <span className="eyebrow">Why this matters now</span>
              <p>{task.summary}</p>
            </div>

            <div className="note-block">
              <span className="eyebrow">Next action</span>
              <strong>{task.nextActionLabel}</strong>
              <p>{task.nextActionDetail}</p>
            </div>
          </div>

          <aside className="task-document__aside">
            <article className="signal-block">
              <span className="eyebrow">Connected agent</span>
              <strong>{leadAgent ? `${leadAgent.roleLabel} / ${leadAgent.name}` : "No active agent"}</strong>
              <p>{leadAgent?.responsibility ?? "Choose the role that should continue the task."}</p>
            </article>

            <article className="signal-block signal-block--muted">
              <span className="eyebrow">Shared with team</span>
              <strong>{shareSnapshot?.label ?? "Not staged yet"}</strong>
              <p>{shareSnapshot?.detail ?? "The share state will appear after review and operator confirmation."}</p>
            </article>

            <div className="stacked-meta">
              <span>Account / {task.account}</span>
              <span>Due / {task.dueLabel}</span>
              <span>Updated / {task.updatedAt}</span>
            </div>
          </aside>
        </div>

        <div className="task-document__actions">
          <button className="button button--primary button--wide" onClick={onContinue} type="button">
            {task.nextActionLabel}
          </button>
          <button className="button button--secondary" onClick={onOpenContext} type="button">
            Open context
          </button>
        </div>
      </article>
    </section>
  );
}
