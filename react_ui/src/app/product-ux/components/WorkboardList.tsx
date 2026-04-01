import { TaskRecord } from "../types";

interface WorkboardListProps {
  activeTaskId: string;
  onSelectTask: (taskId: string) => void;
  tasks: TaskRecord[];
}

export function WorkboardList({ activeTaskId, onSelectTask, tasks }: WorkboardListProps) {
  const orderedTasks = [...tasks].sort((left, right) => Number(right.isPrimaryDemo) - Number(left.isPrimaryDemo));

  return (
    <section className="drawer-panel">
      <div className="section-heading section-heading--row">
        <div>
          <span className="eyebrow">작업 선택</span>
          <h3>한 번에 한 작업씩 이어서 진행합니다</h3>
        </div>
        <span className="counter">{tasks.length}</span>
      </div>

      <div className="workboard-list">
        {orderedTasks.map((task) => {
          const shareSnapshot = task.shareStatuses[0];

          return (
            <button
              key={task.id}
              className={task.id === activeTaskId ? "workboard-item is-active" : "workboard-item"}
              onClick={() => onSelectTask(task.id)}
              type="button"
            >
              <div className="workboard-item__topline">
                <div className="workboard-item__title">
                  <strong>{task.title}</strong>
                  {task.isPrimaryDemo ? <span className="state-chip state-chip--primary">메인 데모</span> : null}
                </div>
                <span className="state-chip state-chip--neutral">{task.stageLabel}</span>
              </div>
              <p>{task.summary}</p>
              <div className="workboard-item__meta">
                <span>다음 / {task.nextActionLabel}</span>
                <span>일정 / {task.dueLabel}</span>
              </div>
              <small>{shareSnapshot?.label ?? "공유 상태가 아직 준비되지 않았습니다"}</small>
            </button>
          );
        })}
      </div>
    </section>
  );
}
