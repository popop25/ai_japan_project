import { TaskRecord } from "../types";

interface ReviewSummaryProps {
  task: TaskRecord;
}

export function ReviewSummary({ task }: ReviewSummaryProps) {
  return (
    <section className="review-document">
      <div className="section-header">검토 요약</div>

      <div className="props props--compact">
        <article className="prop">
          <div className="prop-label">검토 결과</div>
          <div className="prop-value">{task.reviewHeadline}</div>
          <div className="prop-value muted">{task.reviewSummary}</div>
        </article>

        <div className="prop-divider" />

        <article className="prop">
          <div className="prop-label">운영자 판단</div>
          <div className="prop-value">{task.operatorDecisionLabel}</div>
          <div className="prop-value muted">{task.operatorDecisionDetail}</div>
        </article>

        <div className="prop-divider" />

        <article className="prop">
          <div className="prop-label">팀 공유 전 확인</div>
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
