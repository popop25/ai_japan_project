import { ResultInbox } from "../components/ResultInbox";
import { ReviewSummary } from "../components/ReviewSummary";
import { SourceOfTruthPanel } from "../components/SourceOfTruthPanel";
import { TaskActionId, TaskRecord } from "../types";

interface ReviewResultScreenProps {
  onOpenContext: () => void;
  onTriggerAction: (actionId: TaskActionId) => void;
  task: TaskRecord;
}

function taskReference(task: TaskRecord): string {
  return task.sources.find((source) => source.type === "Jira")?.title ?? task.id.toUpperCase();
}

export function ReviewResultScreen({ onOpenContext, onTriggerAction, task }: ReviewResultScreenProps) {
  const primaryAction = task.actions.find((action) => action.kind === "primary");
  const reviewStateLabel =
    task.displayState === "shared" ? "공유 완료" : task.reviewOutcomeState === "revise" ? "수정 필요" : "판단 필요";
  const reviewDescription =
    task.displayState === "shared"
      ? "최종 요약이 이미 공유된 상태입니다. Jira와 Confluence에서 팀이 같은 내용을 보는지 확인합니다."
      : "돌아온 결과를 검토하고, 지금 공유할지 여부를 판단해 팀 공유 상태를 확정합니다.";

  return (
    <section className="review-screen">
      <header className="title-block">
        <div className="eyebrow-row">
          <span className="task-id">{taskReference(task)}</span>
          <span className="status-pill">
            <span className="status-dot" />
            {reviewStateLabel}
          </span>
          <span className="sprint-tag">검토 및 공유</span>
        </div>

        <h2 className="task-h1">{task.title}</h2>
        <p className="task-desc">{reviewDescription}</p>
      </header>

      <section className="col-main">
        <ReviewSummary task={task} />

        <div className="action-row">
          {primaryAction ? (
            <button className="button button--primary button--wide" onClick={() => onTriggerAction(primaryAction.id)} type="button">
              {primaryAction.label}
            </button>
          ) : null}
          <button className="button button--secondary" onClick={onOpenContext} type="button">
            맥락 열기
          </button>
        </div>

        <ResultInbox task={task} />
      </section>

      <aside className="col-aside">
        <SourceOfTruthPanel task={task} />
      </aside>
    </section>
  );
}
