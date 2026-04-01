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
    task.displayState === "shared" ? "Shared" : task.reviewOutcomeState === "revise" ? "Revise needed" : "Decision needed";
  const reviewDescription =
    task.displayState === "shared"
      ? "The final summary is already shared. Use this view to confirm the team sees the same update across Jira and Confluence."
      : "Review what came back, decide whether to share now, and lock the team-facing update.";

  return (
    <section className="review-screen">
      <header className="title-block">
        <div className="eyebrow-row">
          <span className="task-id">{taskReference(task)}</span>
          <span className="status-pill">
            <span className="status-dot" />
            {reviewStateLabel}
          </span>
          <span className="sprint-tag">Review &amp; Share</span>
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
            Open context
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
