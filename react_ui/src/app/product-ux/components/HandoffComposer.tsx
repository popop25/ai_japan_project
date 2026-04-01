import * as RadioGroup from "@radix-ui/react-radio-group";

import { HandoffMode, TaskActionId, TaskRecord } from "../types";

interface HandoffComposerProps {
  onChangeHandoffMode: (mode: HandoffMode) => void;
  onOpenContext: () => void;
  onTriggerAction: (actionId: TaskActionId) => void;
  task: TaskRecord;
}

function taskReference(task: TaskRecord): string {
  return task.sources.find((source) => source.type === "Jira")?.title ?? task.id.toUpperCase();
}

export function HandoffComposer({ onChangeHandoffMode, onOpenContext, onTriggerAction, task }: HandoffComposerProps) {
  const primaryAction = task.actions.find((action) => action.kind === "primary");
  const activeAgent = task.connectedAgents.find((agent) => agent.roleId === task.activeBrief.roleId) ?? task.connectedAgents[0];

  return (
    <section className="handoff-screen">
      <header className="title-block">
        <div className="eyebrow-row">
          <span className="task-id">{taskReference(task)}</span>
          <span className="status-pill">
            <span className="status-dot" />
            {task.stageLabel}
          </span>
          <span className="sprint-tag">{task.activeBrief.roleLabel}</span>
        </div>

        <h2 className="task-h1">{task.activeBrief.title}</h2>
        <p className="task-desc">{task.activeBrief.instruction}</p>
      </header>

      <section className="col-main">
        <div className="section-header">Brief to send</div>

        <article className="handoff-doc-sheet">
          <pre className="handoff-brief-body">{task.activeBrief.body}</pre>
        </article>

        <section className="handoff-subsection">
          <div className="section-header">Response expectation</div>
          <div className="props props--compact">
            <article className="prop">
              <div className="prop-label">Expected response</div>
              <div className="prop-value">{task.activeBrief.expectedResponse}</div>
            </article>

            <div className="prop-divider" />

            <article className="prop">
              <div className="prop-label">Before you send</div>
              <ul className="review-checklist review-checklist--compact">
                {task.activeBrief.checklist.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>

            <div className="prop-divider" />

            <article className="prop">
              <div className="prop-label">Context included</div>
              <div className="prop-value muted">{task.activeBrief.contextIncluded.join(", ")}</div>
            </article>
          </div>
        </section>

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
      </section>

      <aside className="col-aside">
        <div className="aside-stack">
          <section className="aside-section">
            <div className="aside-label">Handoff mode</div>
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
          </section>

          <section className="aside-section">
            <div className="aside-label">Send with</div>
            <div className="status-block-list">
              <article className="status-block">
                <span className="eyebrow">Active agent</span>
                <strong>{activeAgent ? `${activeAgent.name} / ${activeAgent.productLabel}` : task.activeBrief.roleLabel}</strong>
                <p>{activeAgent?.statusNote ?? "Use your connected agent for this role."}</p>
              </article>

              <article className="status-block">
                <span className="eyebrow">Bring back</span>
                <strong>{task.activeBrief.expectedResponse}</strong>
                <p>Return with the result before moving to review or the next decision.</p>
              </article>

              <article className="status-block status-block--muted">
                <span className="eyebrow">Manual handoff</span>
                <strong>{task.handoffMode === "file_handoff" ? "Return with the saved response file." : "Paste the returned reply back into the workspace."}</strong>
                <p>
                  {task.handoffMode === "file_handoff"
                    ? `Use the brief file path and bring back ${task.activeBrief.responsePath}.`
                    : "Paste this brief into your own agent chat, then continue once the response is ready."}
                </p>
              </article>
            </div>
          </section>
        </div>
      </aside>
    </section>
  );
}
