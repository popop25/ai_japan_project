import { TaskRecord } from "../types";

interface WorkboardListProps {
  activeTaskId: string;
  onSelectTask: (taskId: string) => void;
  tasks: TaskRecord[];
}

export function WorkboardList({ activeTaskId, onSelectTask, tasks }: WorkboardListProps) {
  return (
    <section className="drawer-panel">
      <div className="section-heading section-heading--row">
        <div>
          <span className="eyebrow">Task picker</span>
          <h3>Continue one task at a time</h3>
        </div>
        <span className="counter">{tasks.length}</span>
      </div>

      <div className="workboard-list">
        {tasks.map((task) => {
          const shareSnapshot = task.shareStatuses[0];

          return (
            <button
              key={task.id}
              className={task.id === activeTaskId ? "workboard-item is-active" : "workboard-item"}
              onClick={() => onSelectTask(task.id)}
              type="button"
            >
              <div className="workboard-item__topline">
                <strong>{task.title}</strong>
                <span className="state-chip state-chip--neutral">{task.stageLabel}</span>
              </div>
              <p>{task.summary}</p>
              <div className="workboard-item__meta">
                <span>Next / {task.nextActionLabel}</span>
                <span>Due / {task.dueLabel}</span>
              </div>
              <small>{shareSnapshot?.label ?? "Share state not staged yet"}</small>
            </button>
          );
        })}
      </div>
    </section>
  );
}
