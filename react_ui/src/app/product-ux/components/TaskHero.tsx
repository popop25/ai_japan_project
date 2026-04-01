import { TaskRecord } from "../types";

interface TaskHeroProps {
  task: TaskRecord;
}

function taskReference(task: TaskRecord): string {
  return task.sources.find((source) => source.type === "Jira")?.title ?? task.id.toUpperCase();
}

export function TaskHero({ task }: TaskHeroProps) {
  return (
    <>
      <header className="title-block">
        <div className="eyebrow-row">
          <span className="task-id">{taskReference(task)}</span>
          <span className="status-pill">
            <span className="status-dot" />
            {task.stageLabel}
          </span>
          <span className="sprint-tag">{task.dueLabel}</span>
        </div>

        <h2 className="task-h1">{task.title}</h2>
        <p className="task-desc">{task.objective}</p>
      </header>

      <section className="col-main">
        <div className="section-header">Task context</div>

        <div className="props">
          <article className="prop">
            <div className="prop-label">Project</div>
            <div className="prop-value">{task.account}</div>
          </article>

          <div className="prop-divider" />

          {task.contextEntries.map((entry) => (
            <article key={entry.id} className="prop">
              <div className="prop-label">{entry.label}</div>
              <div className="prop-value muted">{entry.value}</div>
            </article>
          ))}

          <div className="prop-divider" />

          <article className="prop">
            <div className="prop-label">Output expectation</div>
            <div className="prop-value">{task.activeBrief.expectedResponse}</div>
            <div className="prop-value muted">Shared with the team once the operator confirms the final step.</div>
          </article>

          <div className="prop-divider" />

          <article className="prop">
            <div className="prop-label">Reference notes</div>
            <div className="file-list">
              {task.sources.map((source) => (
                <article key={source.id} className="file-row">
                  <span className="file-icon">{source.type === "Confluence" ? "DOC" : source.type === "Jira" ? "JIRA" : "NOTE"}</span>
                  <span className="file-name">{source.title}</span>
                  <span className="file-meta">{source.freshness}</span>
                  <span className="file-arrow">&gt;</span>
                </article>
              ))}
            </div>
          </article>
        </div>
      </section>
    </>
  );
}
