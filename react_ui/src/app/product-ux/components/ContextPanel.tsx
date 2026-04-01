import { TaskRecord } from "../types";

interface ContextPanelProps {
  task: TaskRecord;
}

export function ContextPanel({ task }: ContextPanelProps) {
  return (
    <section className="drawer-panel">
      <div className="section-heading">
        <span className="eyebrow">Context</span>
        <h3>What this task is grounded in</h3>
      </div>

      <div className="context-list">
        {task.contextEntries.map((entry) => (
          <article key={entry.id} className="context-item">
            <span className="eyebrow">{entry.label}</span>
            <strong>{entry.value}</strong>
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
