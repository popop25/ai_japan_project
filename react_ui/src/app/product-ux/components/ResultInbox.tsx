import { TaskRecord } from "../types";

interface ResultInboxProps {
  task: TaskRecord;
}

function resultStatusLabel(status: TaskRecord["results"][number]["status"]) {
  switch (status) {
    case "ready":
      return "초안 수신";
    case "review":
      return "검토 수신";
    case "pending":
      return "대기 중";
    default:
      return status;
  }
}

export function ResultInbox({ task }: ResultInboxProps) {
  return (
    <section className="review-results">
      <div className="section-header">돌아온 결과</div>

      <div className="result-document-list">
        {task.results.length > 0 ? (
          task.results.map((result) => (
            <article key={result.id} className="result-document-item">
              <div className="result-document-item__topline">
                <div>
                  <span className="prop-label">작업 주체</span>
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
            <strong>아직 확인된 작업 결과가 없습니다.</strong>
            <p>이 작업 공간은 다음 결과가 사용자의 에이전트에서 준비되기를 기다리고 있습니다.</p>
          </article>
        )}
      </div>
    </section>
  );
}
