import { AgentConnectionPanel } from "../components/AgentConnectionPanel";
import { TaskHero } from "../components/TaskHero";
import { TaskRecord } from "../types";

interface TaskDetailScreenProps {
  onContinue: () => void;
  onOpenContext: () => void;
  task: TaskRecord;
}

export function TaskDetailScreen({ onContinue, onOpenContext, task }: TaskDetailScreenProps) {
  return (
    <div className="screen-stack">
      <TaskHero onContinue={onContinue} onOpenContext={onOpenContext} task={task} />
      <AgentConnectionPanel task={task} />
    </div>
  );
}
