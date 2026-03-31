import { ProductExperience, TaskRecord } from "../types";
import { ResultInbox } from "../components/ResultInbox";
import { WorkboardList } from "../components/WorkboardList";

interface TaskInboxWorkboardScreenProps {
  onOpenTask: (taskId: string) => void;
  product: ProductExperience;
  task: TaskRecord;
}

export function TaskInboxWorkboardScreen({ onOpenTask, product, task }: TaskInboxWorkboardScreenProps) {
  return (
    <div className="screen-grid screen-grid--workboard">
      <WorkboardList activeTaskId={task.id} onSelectTask={onOpenTask} tasks={product.tasks} />
      <ResultInbox agents={product.agents} task={task} />
    </div>
  );
}

