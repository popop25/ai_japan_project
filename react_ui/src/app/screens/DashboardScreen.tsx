import { ProductData, PrototypeScreenState, ViewId } from "../../types";
import { ActionPanel } from "../../design-system/components/ActionPanel";
import { ArtifactSummary } from "../../design-system/components/ArtifactSummary";
import { FocusBar } from "../../design-system/components/FocusBar";
import { InlineNotice } from "../../design-system/components/InlineNotice";
import { ProofPanel } from "../../design-system/components/ProofPanel";
import { ScreenStatePanel } from "../../design-system/components/ScreenStatePanel";
import { TaskSwitcher } from "../../design-system/components/TaskSwitcher";
import { TimelinePanel } from "../../design-system/components/TimelinePanel";
import { WorkflowStepper } from "../../design-system/components/WorkflowStepper";

interface DashboardScreenProps {
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

export function DashboardScreen({ data, onNavigate, state = "ready", onResetState }: DashboardScreenProps) {
  if (state === "loading") {
    return (
      <ScreenStatePanel
        description="The overview is waiting for queue, current workflow, and proof metadata to settle."
        detail="Keep the first fold stable while fixture payloads are swapped for a live overview endpoint later."
        eyebrow="Overview"
        highlights={[
          "Current action must stay readable before secondary summaries.",
          "Proof area should tolerate missing Jira or Confluence links.",
          "The operator still needs a clear next surface to open.",
        ]}
        title="Loading operator overview"
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
            <button className="button button--secondary" onClick={() => onNavigate("workflow")} type="button">
              Open workflow detail
            </button>
          </div>
        }
        description="Overview data did not render safely."
        detail="Fail in place without inventing fallback workflow state in the client."
        eyebrow="Overview"
        highlights={[
          "Keep IA intact even when shell data fails.",
          "Do not simulate packet or proof state in the frontend.",
        ]}
        title="Overview unavailable"
        state="error"
      />
    );
  }

  const activeTask = data.queue.find((item) => item.jiraKey === data.workflow.currentTaskId) ?? data.queue[0] ?? null;
  const isEmptyDashboard = state === "empty" || !activeTask;

  if (isEmptyDashboard) {
    return (
      <ScreenStatePanel
        actions={
          <div className="button-row">
            <button className="button button--primary" onClick={() => onNavigate("context")} type="button">
              Open context
            </button>
            <button className="button button--secondary" onClick={() => onNavigate("workflow")} type="button">
              Open workflow detail
            </button>
          </div>
        }
        description="There is no active task to operate yet."
        detail="The screen should point the operator to context or workflow setup instead of collapsing into empty summary cards."
        eyebrow="Overview"
        highlights={[
          "Keep first fold action-oriented even in empty state.",
          "Do not imply a live queue when fixture data is absent.",
        ]}
        title="No active workflow"
        state="empty"
      />
    );
  }

  const proofArtifact =
    data.artifacts.find((artifact) => artifact.linkedTask === activeTask.jiraKey && artifact.status === activeTask.status) ??
    data.artifacts.find((artifact) => artifact.linkedTask === activeTask.jiraKey) ??
    data.artifacts[0];

  return (
    <div className="cp-stack cp-stack--xl">
      <div className="overview-first-fold">
        <FocusBar
          currentStage={data.overview.currentStage}
          onPrimaryAction={() => onNavigate("workflow")}
          onSecondaryAction={() => onNavigate("artifacts")}
          primaryLabel="Open workflow detail"
          secondaryLabel="Review blocking artifact"
          task={activeTask}
        />
        <WorkflowStepper steps={data.workflow.steps} />
        <ProofPanel artifact={proofArtifact} connections={data.connections} task={activeTask} />
      </div>

      <div className="overview-grid">
        <TaskSwitcher activeTaskId={data.workflow.currentTaskId} items={data.queue} onNavigate={onNavigate} />

        <ActionPanel
          description="The first operator read should be a decision list, not a KPI wall."
          eyebrow="Operator priorities"
          title={data.overview.nextActionTitle}
          tone="warning"
          actions={
            <button className="button button--primary" onClick={() => onNavigate("workflow")} type="button">
              Dispatch next step
            </button>
          }
        >
          <p>{data.overview.nextActionBody}</p>
          <div className="cp-stack cp-stack--tight">
            {data.metrics.map((metric) => (
              <div className="signal-row" key={metric.label}>
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
                <p>{metric.detail}</p>
              </div>
            ))}
          </div>
        </ActionPanel>
      </div>

      <div className="content-grid content-grid--two">
        <TimelinePanel eyebrow="Latest signals" items={data.activity} title="Activity timeline" />
        {proofArtifact ? (
          <ArtifactSummary artifact={proofArtifact} title="Primary review surface" />
        ) : (
          <InlineNotice
            description="Artifact review will appear here once the backend publishes the current draft or review payload."
            title="No artifact summary is available"
          />
        )}
      </div>
    </div>
  );
}
