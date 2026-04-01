import { TaskRecord } from "../types";

interface ResultInboxProps {
  task: TaskRecord;
}

function resultStatusLabel(status: TaskRecord["results"][number]["status"]) {
  switch (status) {
    case "ready":
      return "Draft received";
    case "review":
      return "Review received";
    case "pending":
      return "Waiting";
    default:
      return status;
  }
}

export function ResultInbox({ task }: ResultInboxProps) {
  return (
    <section className="panel panel--muted">
      <div className="section-heading section-heading--row">
        <div>
          <span className="eyebrow">Latest results</span>
          <h3>What came back from the agents</h3>
        </div>
        <span className="counter">{task.results.length}</span>
      </div>

      <div className="result-list">
        {task.results.length > 0 ? (
          task.results.map((result) => (
            <article key={result.id} className="result-item">
              <div className="result-item__topline">
                <strong>{result.title}</strong>
                <span className={`state-chip state-chip--${result.status}`}>{resultStatusLabel(result.status)}</span>
              </div>
              <p>{result.summary}</p>
              <div className="result-item__meta">
                <span>{result.fromAgentLabel}</span>
                <span>{result.updatedAt}</span>
              </div>
            </article>
          ))
        ) : (
          <article className="result-item result-item--empty">
            <strong>No response has been received yet.</strong>
            <p>The workspace is still waiting for the next result to come back from your agent.</p>
          </article>
        )}
      </div>
    </section>
  );
}
