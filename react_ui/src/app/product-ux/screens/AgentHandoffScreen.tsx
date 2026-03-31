import { AgentConnectionPanel } from "../components/AgentConnectionPanel";
import { HandoffComposer } from "../components/HandoffComposer";
import { SourceOfTruthPanel } from "../components/SourceOfTruthPanel";
import { ProductExperience, TaskRecord } from "../types";

interface AgentHandoffScreenProps {
  onOpenReview: () => void;
  product: ProductExperience;
  task: TaskRecord;
}

export function AgentHandoffScreen({ onOpenReview, product, task }: AgentHandoffScreenProps) {
  return (
    <div className="screen-grid screen-grid--two-one">
      <div className="screen-stack">
        <HandoffComposer agents={product.agents} task={task} />
        <div className="inline-action-row">
          <button className="agent-button is-primary" onClick={onOpenReview} type="button">
            Critic에 검토 요청
          </button>
          <button className="agent-button" type="button">
            초안 받기
          </button>
        </div>
      </div>
      <div className="screen-stack">
        <AgentConnectionPanel agents={product.agents} task={task} />
        <SourceOfTruthPanel task={task} />
      </div>
    </div>
  );
}

