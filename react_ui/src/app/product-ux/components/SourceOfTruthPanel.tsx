import { TaskRecord } from "../types";

interface SourceOfTruthPanelProps {
  task: TaskRecord;
}

export function SourceOfTruthPanel({ task }: SourceOfTruthPanelProps) {
  const teamDestinations = task.sources.filter((source) => source.type === "Jira" || source.type === "Confluence");
  const isShared = task.displayState === "shared";

  return (
    <div className="aside-stack">
      <section className="aside-section">
        <div className="aside-label">팀 공유 상태</div>
        <div className="share-rail">
          {task.shareStatuses.map((status) => (
            <article key={status.system} className={`share-rail-card share-rail-card--${status.tone}`}>
              <div className="share-rail-card__header">
                <strong>{status.system}</strong>
                <span className={`state-chip state-chip--${status.tone === "healthy" ? "connected" : status.tone}`}>{status.label}</span>
              </div>
              <p>{status.detail}</p>
              <span className="share-rail-card__updated">{status.updatedAt}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="aside-section">
        <div className="aside-label">공유 대상</div>
        <div className="destination-list">
          {(teamDestinations.length > 0 ? teamDestinations : task.sources).map((source) => (
            <article key={source.id} className="destination-card">
              <div className="destination-card__topline">
                <span className="prop-label">{source.type}</span>
                <span className="file-meta">{source.freshness}</span>
              </div>
              <strong>{source.title}</strong>
              <p>{source.note}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="aside-section">
        <div className="aside-label">워크플로우</div>
        <div className="wf-list">
          <div className="wf-row">
            <span className="wf-num">01</span>
            <span className="wf-name">작업</span>
            <span className="wf-marker">완료</span>
          </div>
          <div className="wf-row">
            <span className="wf-num">02</span>
            <span className="wf-name">에이전트 전달</span>
            <span className="wf-marker">완료</span>
          </div>
          <div className={isShared ? "wf-row complete" : "wf-row current"}>
            <span className="wf-num">03</span>
            <span className="wf-name">검토 및 공유</span>
            <span className="wf-marker">{isShared ? "완료" : "현재"}</span>
          </div>
        </div>
      </section>
    </div>
  );
}
