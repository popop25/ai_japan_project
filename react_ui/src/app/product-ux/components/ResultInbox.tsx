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
    <section className="review-results">
      <div className="section-header">Returned items</div>

      <div className="result-document-list">
        {task.results.length > 0 ? (
          task.results.map((result) => (
            <article key={result.id} className="result-document-item">
              <div className="result-document-item__topline">
                <div>
                  <span className="prop-label">Returned by</span>
                  <div className="result-document-item__title">{result.title}</div>
                </div>
                <span className={`state-chip state-chip--${result.status}`}>{resultStatusLabel(result.status)}</span>
              </div>
              <p className="prop-value muted">{result.summary}</p>
              <div className="result-document-item__meta">
                <span>{result.fromAgentLabel}</span>
                <span>{result.updatedAt}</span>
              </div>
            </article>
          ))
        ) : (
          <article className="result-document-item result-document-item--empty">
            <strong>No response has been received yet.</strong>
            <p>The workspace is still waiting for the next result to come back from your agent.</p>
          </article>
        )}
      </div>
    </section>
  );
}
