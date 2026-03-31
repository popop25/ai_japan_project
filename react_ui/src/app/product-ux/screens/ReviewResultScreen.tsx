import { ResultInbox } from "../components/ResultInbox";
import { ReviewSummary } from "../components/ReviewSummary";
import { SourceOfTruthPanel } from "../components/SourceOfTruthPanel";
import { ProductExperience, TaskRecord } from "../types";

interface ReviewResultScreenProps {
  onOpenTask: () => void;
  product: ProductExperience;
  task: TaskRecord;
}

export function ReviewResultScreen({ onOpenTask, product, task }: ReviewResultScreenProps) {
  return (
    <div className="screen-stack">
      <ReviewSummary task={task} />
      <div className="inline-action-row">
        <button className="agent-button is-primary" onClick={onOpenTask} type="button">
          검토 결과 반영
        </button>
        <button className="agent-button" type="button">
          팀 공유 상태 확인
        </button>
      </div>
      <div className="screen-grid">
        <ResultInbox agents={product.agents} task={task} />
        <SourceOfTruthPanel task={task} />
      </div>
    </div>
  );
}

