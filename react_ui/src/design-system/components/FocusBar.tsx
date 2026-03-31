import { QueueItem } from "../../types";
import { Chip } from "./Chip";
import { StatusBadge } from "./StatusBadge";

interface FocusBarProps {
  task: QueueItem;
  currentStage: string;
  primaryLabel: string;
  secondaryLabel?: string;
  onPrimaryAction: () => void;
  onSecondaryAction?: () => void;
}

export function FocusBar({
  task,
  currentStage,
  primaryLabel,
  secondaryLabel,
  onPrimaryAction,
  onSecondaryAction,
}: FocusBarProps) {
  return (
    <section className="focus-bar">
      <div className="focus-bar__head">
        <div>
          <p className="eyebrow">Current action</p>
          <h3>{task.nextAction}</h3>
        </div>
        <StatusBadge status={task.status} />
      </div>

      <div className="focus-bar__grid">
        <div className="focus-bar__cell focus-bar__cell--task">
          <span>Current task</span>
          <strong>
            {task.jiraKey} ¡¤ {task.title}
          </strong>
        </div>
        <div className="focus-bar__cell">
          <span>Current stage</span>
          <strong>{currentStage}</strong>
        </div>
        <div className="focus-bar__cell">
          <span>Owner</span>
          <strong>{task.owner}</strong>
        </div>
        <div className="focus-bar__cell">
          <span>Artifacts</span>
          <strong>{task.artifactCount}</strong>
        </div>
      </div>

      <div className="focus-bar__footer">
        <div className="chip-row">
          <Chip label={`Updated ${task.updatedAt}`} tone="neutral" />
          <Chip label="Fixture-backed UI" tone="warning" />
        </div>
        <div className="button-row">
          <button className="button button--primary" onClick={onPrimaryAction} type="button">
            {primaryLabel}
          </button>
          {secondaryLabel && onSecondaryAction ? (
            <button className="button button--secondary" onClick={onSecondaryAction} type="button">
              {secondaryLabel}
            </button>
          ) : null}
        </div>
      </div>
    </section>
  );
}
