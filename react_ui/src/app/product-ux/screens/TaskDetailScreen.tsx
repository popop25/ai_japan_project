import { AgentConnectionPanel } from "../components/AgentConnectionPanel";
import { TaskHero } from "../components/TaskHero";
import { TaskRecord } from "../types";

interface TaskDetailScreenProps {
  onContinue: () => void;
  task: TaskRecord;
}

export function TaskDetailScreen({ onContinue, task }: TaskDetailScreenProps) {
  return (
    <div className="task-screen">
      <TaskHero task={task} />
      <aside className="col-aside">
        <AgentConnectionPanel onContinue={onContinue} task={task} />
      </aside>
    </div>
  );
}
