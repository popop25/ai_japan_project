import { TaskRecord } from "../types";

interface ReviewSummaryProps {
  task: TaskRecord;
}

export function ReviewSummary({ task }: ReviewSummaryProps) {
  return (
    <section className="review-document">
      <div className="section-header">Review summary</div>

      <div className="props props--compact">
        <article className="prop">
          <div className="prop-label">Review outcome</div>
          <div className="prop-value">{task.reviewHeadline}</div>
          <div className="prop-value muted">{task.reviewSummary}</div>
        </article>

        <div className="prop-divider" />

        <article className="prop">
          <div className="prop-label">Operator decision</div>
          <div className="prop-value">{task.operatorDecisionLabel}</div>
          <div className="prop-value muted">{task.operatorDecisionDetail}</div>
        </article>

        <div className="prop-divider" />

        <article className="prop">
          <div className="prop-label">Before team share</div>
          <ul className="review-checklist">
          {task.reviewChecklist.map((item) => (
            <li key={item}>{item}</li>
          ))}
          </ul>
        </article>
      </div>
    </section>
  );
}
