import { ResultInbox } from "../components/ResultInbox";
import { ReviewSummary } from "../components/ReviewSummary";
import { SourceOfTruthPanel } from "../components/SourceOfTruthPanel";
import { TaskActionId, TaskRecord } from "../types";

interface ReviewResultScreenProps {
  onOpenContext: () => void;
  onTriggerAction: (actionId: TaskActionId) => void;
  task: TaskRecord;
}

export function ReviewResultScreen({ onOpenContext, onTriggerAction, task }: ReviewResultScreenProps) {
  const primaryAction = task.actions.find((action) => action.kind === "primary");

  return (
    <div className="review-layout">
      <div className="screen-stack">
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
      </div>

      <SourceOfTruthPanel task={task} />
    </div>
  );
}
