import { QueueItem, ViewId } from "../../types";
import { cx } from "../../utils";
import { StatusBadge } from "./StatusBadge";

interface TaskSwitcherProps {
  items: QueueItem[];
  activeTaskId: string;
  onNavigate: (view: ViewId) => void;
}

function targetViewForTask(task: QueueItem): ViewId {
  return task.status === "review_requested" ? "artifacts" : "workflow";
}

export function TaskSwitcher({ items, activeTaskId, onNavigate }: TaskSwitcherProps) {
  return (
    <section className="surface">
      <div className="surface__head">
        <div>
          <p className="eyebrow">Task switcher</p>
          <h3>Operator queue</h3>
        </div>
      </div>
      <div className="task-switcher">
        {items.map((item) => {
          const isActive = item.jiraKey === activeTaskId;
          return (
            <button
              className={cx("task-switcher__item", isActive && "task-switcher__item--active")}
              key={item.id}
              onClick={() => onNavigate(targetViewForTask(item))}
              type="button"
            >
              <div className="task-switcher__top">
                <div>
                  <span className="task-switcher__key">{item.jiraKey}</span>
                  <strong>{item.title}</strong>
                </div>
                <StatusBadge status={item.status} />
              </div>
              <div className="task-switcher__meta">
                <span>{item.stage}</span>
                <span>{item.updatedAt}</span>
                <span>{item.artifactCount} artifacts</span>
              </div>
              <p>{item.nextAction}</p>
            </button>
          );
        })}
      </div>
    </section>
  );
}
