import { TaskRecord } from "../types";

interface SourceOfTruthPanelProps {
  task: TaskRecord;
}

export function SourceOfTruthPanel({ task }: SourceOfTruthPanelProps) {
  return (
    <section className="agent-panel">
      <div className="agent-panel__header">
        <div>
          <span className="agent-kicker">Source of truth</span>
          <h3>팀에 공유되는 기준 문서</h3>
        </div>
      </div>
      <div className="source-list">
        {task.shareStatuses.map((status) => (
          <article key={status.system} className="source-item">
            <div>
              <strong>{status.system}</strong>
              <p>{status.label}</p>
            </div>
            <span>{status.detail}</span>
          </article>
        ))}
        {task.sources.map((source) => (
          <article key={source.id} className="source-item source-item--document">
            <div>
              <strong>{source.title}</strong>
              <p>{source.type} · {source.freshness}</p>
            </div>
            <span>{source.note}</span>
          </article>
        ))}
      </div>
    </section>
  );
}

