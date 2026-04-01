import { TaskRecord } from "../types";

interface ReviewSummaryProps {
  task: TaskRecord;
}

export function ReviewSummary({ task }: ReviewSummaryProps) {
  const outcomeLabel = task.reviewOutcomeState === "revise" ? "Revise needed" : "Operator decision needed";

  return (
    <section className="panel review-summary">
      <div className="section-heading section-heading--row">
        <div>
          <span className="eyebrow">Review & Share</span>
          <h2>{task.reviewHeadline}</h2>
        </div>
        <span className={`state-chip ${task.reviewOutcomeState === "revise" ? "state-chip--attention" : "state-chip--primary"}`}>
          {outcomeLabel}
        </span>
      </div>

      <p className="task-document__summary">{task.reviewSummary}</p>

      <div className="decision-card">
        <span className="eyebrow">Operator decision</span>
        <strong>{task.operatorDecisionLabel}</strong>
        <p>{task.operatorDecisionDetail}</p>
      </div>

      <div className="checklist-block">
        <span className="eyebrow">Before the next step</span>
        <ul>
          {task.reviewChecklist.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
