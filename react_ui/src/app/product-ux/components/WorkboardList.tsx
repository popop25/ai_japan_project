import { TaskRecord } from "../types";

interface WorkboardListProps {
  activeTaskId: string;
  onSelectTask: (taskId: string) => void;
  tasks: TaskRecord[];
}

export function WorkboardList({ activeTaskId, onSelectTask, tasks }: WorkboardListProps) {
  return (
    <section className="agent-panel">
      <div className="agent-panel__header">
        <div>
          <span className="agent-kicker">Task Inbox / Workboard</span>
          <h3>지금 이어서 처리할 task</h3>
        </div>
        <span className="agent-counter">{tasks.length} open tasks</span>
      </div>
      <div className="workboard-list">
        {tasks.map((task) => (
          <button
            key={task.id}
            className={task.id === activeTaskId ? "workboard-item is-active" : "workboard-item"}
            onClick={() => onSelectTask(task.id)}
            type="button"
          >
            <div className="workboard-item__topline">
              <strong>{task.title}</strong>
              <span>{task.stage}</span>
            </div>
            <p>{task.summary}</p>
            <div className="workboard-item__meta">
              <span>{task.nextActionLabel}</span>
              <span>{task.dueLabel}</span>
              <span>{task.urgency}</span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}

