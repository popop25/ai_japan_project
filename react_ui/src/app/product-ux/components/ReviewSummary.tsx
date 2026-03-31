import { TaskRecord } from "../types";

interface ReviewSummaryProps {
  task: TaskRecord;
}

export function ReviewSummary({ task }: ReviewSummaryProps) {
  return (
    <section className="agent-panel review-summary">
      <div className="agent-panel__header">
        <div>
          <span className="agent-kicker">Review Result</span>
          <h3>{task.reviewHeadline}</h3>
        </div>
      </div>
      <p className="review-summary__body">{task.reviewSummary}</p>
      <div className="review-checklist">
        {task.decisions.map((decision) => (
          <div key={decision.id} className={`review-checklist__item is-${decision.state}`}>
            <strong>{decision.label}</strong>
            <span>{decision.rationale}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

