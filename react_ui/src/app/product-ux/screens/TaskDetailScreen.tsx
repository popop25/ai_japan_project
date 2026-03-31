import { AgentConnectionPanel } from "../components/AgentConnectionPanel";
import { DecisionBar } from "../components/DecisionBar";
import { SourceOfTruthPanel } from "../components/SourceOfTruthPanel";
import { TaskHero } from "../components/TaskHero";
import { ProductExperience, TaskRecord } from "../types";

interface TaskDetailScreenProps {
  onOpenContext: () => void;
  onOpenHandoff: () => void;
  product: ProductExperience;
  task: TaskRecord;
}

export function TaskDetailScreen({ onOpenContext, onOpenHandoff, product, task }: TaskDetailScreenProps) {
  return (
    <div className="screen-stack">
      <TaskHero agents={product.agents} onOpenContext={onOpenContext} onOpenHandoff={onOpenHandoff} task={task} />
      <DecisionBar task={task} />
      <div className="screen-grid">
        <AgentConnectionPanel agents={product.agents} task={task} />
        <SourceOfTruthPanel task={task} />
      </div>
    </div>
  );
}

