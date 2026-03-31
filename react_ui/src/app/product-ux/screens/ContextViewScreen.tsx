import { ContextPanel } from "../components/ContextPanel";
import { DecisionBar } from "../components/DecisionBar";
import { SourceOfTruthPanel } from "../components/SourceOfTruthPanel";
import { ProductExperience, TaskRecord } from "../types";

interface ContextViewScreenProps {
  onOpenTask: () => void;
  product: ProductExperience;
  task: TaskRecord;
}

export function ContextViewScreen({ onOpenTask, task }: ContextViewScreenProps) {
  return (
    <div className="screen-stack">
      <div className="inline-action-row">
        <button className="agent-button is-primary" onClick={onOpenTask} type="button">
          Task로 돌아가기
        </button>
      </div>
      <ContextPanel task={task} />
      <DecisionBar task={task} />
      <SourceOfTruthPanel task={task} />
    </div>
  );
}

