import * as RadioGroup from "@radix-ui/react-radio-group";

import { HandoffMode, TaskActionId, TaskRecord } from "../types";

interface HandoffComposerProps {
  onChangeHandoffMode: (mode: HandoffMode) => void;
  onOpenContext: () => void;
  onTriggerAction: (actionId: TaskActionId) => void;
  task: TaskRecord;
}

export function HandoffComposer({ onChangeHandoffMode, onOpenContext, onTriggerAction, task }: HandoffComposerProps) {
  const primaryAction = task.actions.find((action) => action.kind === "primary");
  const activeAgent = task.connectedAgents.find((agent) => agent.roleId === task.activeBrief.roleId) ?? task.connectedAgents[0];

  return (
    <section className="handoff-layout">
      <article className="panel handoff-document">
        <div className="section-heading section-heading--row">
          <div>
            <span className="eyebrow">Agent handoff</span>
            <h2>{task.activeBrief.title}</h2>
          </div>
          <span className="state-chip state-chip--primary">{task.stageLabel}</span>
        </div>

        <p className="task-document__summary">{task.activeBrief.instruction}</p>

        <div className="handoff-document__body">
          <span className="eyebrow">Brief</span>
          <pre className="handoff-brief-body">{task.activeBrief.body}</pre>
        </div>

        <div className="task-document__actions">
          {primaryAction ? (
            <button className="button button--primary button--wide" onClick={() => onTriggerAction(primaryAction.id)} type="button">
              {primaryAction.label}
            </button>
          ) : null}
          <button className="button button--secondary" onClick={onOpenContext} type="button">
            Open context
          </button>
        </div>
      </article>

      <aside className="panel handoff-side">
        <div className="section-heading">
          <span className="eyebrow">Handoff mode</span>
          <h3>Choose how you will send this brief</h3>
        </div>

        <RadioGroup.Root className="mode-selector" onValueChange={(value) => onChangeHandoffMode(value as HandoffMode)} value={task.handoffMode}>
          {task.handoffModeOptions.map((mode) => (
            <label key={mode.id} className="mode-option">
              <RadioGroup.Item className="mode-option__control" value={mode.id}>
                <RadioGroup.Indicator className="mode-option__indicator" />
              </RadioGroup.Item>
              <div className="mode-option__copy">
                <strong>{mode.label}</strong>
                <span>{mode.helper}</span>
              </div>
            </label>
          ))}
        </RadioGroup.Root>

        <div className="status-block-list">
          <article className="status-block">
            <span className="eyebrow">Send with</span>
            <strong>{activeAgent ? `${activeAgent.name} / ${activeAgent.productLabel}` : task.activeBrief.roleLabel}</strong>
            <p>{activeAgent?.statusNote ?? "Use your connected agent for this role."}</p>
          </article>

          <article className="status-block">
            <span className="eyebrow">Context included</span>
            <strong>{task.activeBrief.contextIncluded.join(", ")}</strong>
            <p>The workspace has already narrowed the context to what this role needs.</p>
          </article>

          <article className="status-block">
            <span className="eyebrow">Expected response</span>
            <strong>{task.activeBrief.expectedResponse}</strong>
            <p>Bring the response back here before moving to the next stage.</p>
          </article>

          <article className="status-block status-block--muted">
            <span className="eyebrow">{task.handoffMode === "file_handoff" ? "File path" : "Paste-back"}</span>
            <strong>{task.handoffMode === "file_handoff" ? task.activeBrief.handoffPath : task.activeBrief.responsePath}</strong>
            <p>The handoff stays manual in this demo, on purpose.</p>
          </article>
        </div>
      </aside>
    </section>
  );
}
