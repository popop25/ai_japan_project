import { ProductData, PrototypeScreenState, QueueItem, ViewId } from "../../types";
import { ActionPanel } from "../../design-system/components/ActionPanel";
import { FocusBar } from "../../design-system/components/FocusBar";
import { InlineNotice } from "../../design-system/components/InlineNotice";
import { ProofPanel } from "../../design-system/components/ProofPanel";
import { ScreenStatePanel } from "../../design-system/components/ScreenStatePanel";
import { TaskSwitcher } from "../../design-system/components/TaskSwitcher";
import { TimelinePanel } from "../../design-system/components/TimelinePanel";
import { WorkflowStepper } from "../../design-system/components/WorkflowStepper";

interface WorkflowWorkspaceScreenProps {
  data: ProductData;
  onNavigate: (view: ViewId) => void;
  state?: PrototypeScreenState;
  onResetState?: () => void;
}

function recoverFixture(onResetState?: () => void) {
  if (onResetState) {
    onResetState();
    return;
  }

  if (typeof window !== "undefined") {
    window.location.reload();
  }
}

function workflowTask(data: ProductData): QueueItem {
  return (
    data.queue.find((item) => item.jiraKey === data.workflow.currentTaskId) ?? {
      artifactCount: 0,
      id: data.workflow.currentTaskId,
      jiraKey: data.workflow.currentTaskId,
      nextAction: data.workflow.steps.find((step) => step.status === "current")?.operatorAction ?? "No operator action published.",
      owner: "Operator",
      stage: data.workflow.steps.find((step) => step.status === "current")?.title ?? data.workflow.title,
      status: data.workflow.currentStatus,
      title: data.workflow.title,
      updatedAt: data.overview.lastUpdated,
    }
  );
}

export function WorkflowWorkspaceScreen({ data, onNavigate, state = "ready", onResetState }: WorkflowWorkspaceScreenProps) {
  if (state === "loading") {
    return (
      <ScreenStatePanel
        description="Workflow detail is waiting for current task, packet contract, and trace data."
        detail="The layout should hold its shape while live task-detail endpoints replace fixture payloads."
        eyebrow="Workflow Detail"
        highlights={[
          "Keep current step readable before packet details load.",
          "Do not derive missing state transitions in the client.",
          "Trace data is supportive, not authoritative.",
        ]}
        title="Loading workflow detail"
        state="loading"
      />
    );
  }

  if (state === "error") {
    return (
      <ScreenStatePanel
        actions={
          <div className="button-row">
            <button className="button button--primary" onClick={() => recoverFixture(onResetState)} type="button">
              Use fixture payload
            </button>
            <button className="button button--secondary" onClick={() => onNavigate("dashboard")} type="button">
              Return to overview
            </button>
          </div>
        }
        description="Workflow detail could not be rendered safely."
        detail="Keep navigation alive and wait for the backend to supply canonical task state."
        eyebrow="Workflow Detail"
        highlights={[
          "State transitions remain in the service layer.",
          "Do not fake packet or review data.",
        ]}
        title="Workflow detail unavailable"
        state="error"
      />
    );
  }

  const workflow = data.workflow;
  const currentStep = workflow.steps.find((step) => step.status === "current") ?? workflow.steps[workflow.steps.length - 1] ?? null;
  const task = workflowTask(data);

  if (state === "empty" || !currentStep) {
    return (
      <ScreenStatePanel
        actions={
          <div className="button-row">
            <button className="button button--primary" onClick={() => onNavigate("dashboard")} type="button">
              Return to overview
            </button>
            <button className="button button--secondary" onClick={() => onNavigate("context")} type="button">
              Review context
            </button>
          </div>
        }
        description="No guided task detail is available."
        detail="An empty workflow screen should redirect the operator to context or queue selection instead of rendering decorative chrome."
        eyebrow="Workflow Detail"
        highlights={[
          "Stepper must tolerate no steps.",
          "Packet view should not invent a contract.",
        ]}
        title="No workflow selected"
        state="empty"
      />
    );
  }

  const proofArtifact = data.artifacts.find((artifact) => artifact.linkedTask === workflow.currentTaskId) ?? data.artifacts[0] ?? null;
  const hasPacketContract =
    Boolean(workflow.packet.title || workflow.packet.audience || workflow.packet.handoffMode || workflow.packet.objective) ||
    workflow.packet.inputs.length > 0 ||
    workflow.packet.outputContract.length > 0 ||
    Boolean(workflow.packet.snippet.trim());

  return (
    <div className="cp-stack cp-stack--xl">
      <FocusBar
        currentStage={currentStep.title}
        onPrimaryAction={() => onNavigate("artifacts")}
        onSecondaryAction={() => onNavigate("dashboard")}
        primaryLabel="Open artifact review"
        secondaryLabel="Return to overview"
        task={{ ...task, nextAction: currentStep.operatorAction }}
      />

      <div className="content-grid content-grid--workflow">
        <WorkflowStepper steps={workflow.steps} />
        <ProofPanel artifact={proofArtifact} connections={data.connections} task={task} title="Jira / Confluence / runtime proof" />
      </div>

      <div className="content-grid content-grid--workflow">
        <ActionPanel
          actions={
            <button className="button button--primary" onClick={() => onNavigate("artifacts")} type="button">
              Inspect returned review
            </button>
          }
          description="The client renders packet contract and handoff choices. State transition logic stays in the backend."
          eyebrow="Dispatch"
          title="Packet + handoff operation"
          tone="brand"
        >
          {hasPacketContract ? (
            <>
              <div className="triple-grid">
                <div className="info-cell">
                  <span>Audience</span>
                  <strong>{workflow.packet.audience}</strong>
                </div>
                <div className="info-cell">
                  <span>Handoff mode</span>
                  <strong>{workflow.packet.handoffMode}</strong>
                </div>
                <div className="info-cell">
                  <span>Objective</span>
                  <strong>{workflow.packet.objective}</strong>
                </div>
              </div>
              <div className="dual-list">
                <div className="surface-block">
                  <span>Inputs</span>
                  <ul className="clean-list">
                    {workflow.packet.inputs.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div className="surface-block">
                  <span>Output contract</span>
                  <ul className="clean-list">
                    {workflow.packet.outputContract.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
              <pre className="packet-snippet">{workflow.packet.snippet}</pre>
            </>
          ) : (
            <InlineNotice
              description="Packet metadata remains empty until the backend supplies the task detail payload."
              title="No packet preview is available"
            />
          )}
        </ActionPanel>

        <ActionPanel
          description="These routes remain operator-selected. The frontend does not simulate a live agent runtime."
          eyebrow="Handoff paths"
          title="External agent options"
        >
          {workflow.handoffModes.map((mode) => (
            <div className="signal-row signal-row--compact" key={mode.name}>
              <span>{mode.name}</span>
              <strong>{mode.fit}</strong>
              <p>{mode.summary}</p>
            </div>
          ))}
        </ActionPanel>
      </div>

      <div className="content-grid content-grid--two">
        <TimelinePanel eyebrow="Traceability" items={workflow.runTrace.map((entry) => ({ detail: entry.detail, status: entry.status, time: entry.time, title: entry.label }))} title="Run trace" />
        <ActionPanel eyebrow="Operator check" title="Next controlled moves">
          {workflow.checklists.length ? (
            workflow.checklists.map((block) => (
              <div className="surface-block" key={block.title}>
                <span>{block.title}</span>
                <ul className="clean-list">
                  {block.items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ))
          ) : (
            <InlineNotice description="Checklist content is not available." title="No operator checklist" />
          )}
        </ActionPanel>
      </div>

      <TaskSwitcher activeTaskId={workflow.currentTaskId} items={data.queue} onNavigate={onNavigate} />
    </div>
  );
}

