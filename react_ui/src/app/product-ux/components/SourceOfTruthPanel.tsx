import { TaskRecord } from "../types";

interface SourceOfTruthPanelProps {
  task: TaskRecord;
}

export function SourceOfTruthPanel({ task }: SourceOfTruthPanelProps) {
  return (
    <section className="panel share-panel">
      <div className="section-heading">
        <span className="eyebrow">Shared with team</span>
        <h3>Jira and Confluence status</h3>
      </div>

      <div className="share-panel__states">
        {task.shareStatuses.map((status) => (
          <article key={status.system} className={`share-state share-state--${status.tone}`}>
            <div>
              <strong>{status.system}</strong>
              <p>{status.label}</p>
            </div>
            <div className="share-state__detail">
              <span>{status.detail}</span>
              <small>{status.updatedAt}</small>
            </div>
          </article>
        ))}
      </div>

      <div className="source-section">
        <span className="eyebrow">Source notes</span>
        <div className="source-list">
          {task.sources.map((source) => (
            <article key={source.id} className="source-item">
              <div>
                <strong>{source.title}</strong>
                <p>
                  {source.type} / {source.freshness}
                </p>
              </div>
              <span>{source.note}</span>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
