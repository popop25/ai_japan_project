import { TaskRecord } from "../types";

interface ContextPanelProps {
  task: TaskRecord;
}

export function ContextPanel({ task }: ContextPanelProps) {
  return (
    <section className="agent-panel">
      <div className="agent-panel__header">
        <div>
          <span className="agent-kicker">Context View</span>
          <h3>내 agent가 읽고 이어받는 맥락</h3>
        </div>
      </div>
      <div className="context-grid">
        {task.contextEntries.map((entry) => (
          <article key={entry.id} className="context-card">
            <span className="agent-mini-label">{entry.label}</span>
            <p>{entry.value}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

