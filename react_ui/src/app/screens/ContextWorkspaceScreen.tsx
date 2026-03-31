import { ProductData, ViewId } from "../../types";
import { ActionPanel } from "../../design-system/components/ActionPanel";
import { FocusBar } from "../../design-system/components/FocusBar";
import { DocView } from "../../design-system/components/DocView";
import { TimelinePanel } from "../../design-system/components/TimelinePanel";

interface ContextWorkspaceScreenProps {
  data: ProductData;
  onNavigate: (view: ViewId) => void;
}

export function ContextWorkspaceScreen({ data, onNavigate }: ContextWorkspaceScreenProps) {
  const activeTask = data.queue.find((item) => item.jiraKey === data.workflow.currentTaskId) ?? data.queue[0] ?? null;

  return (
    <div className="cp-stack cp-stack--xl">
      {activeTask ? (
        <FocusBar
          currentStage="Context checkpoint"
          onPrimaryAction={() => onNavigate("workflow")}
          onSecondaryAction={() => onNavigate("artifacts")}
          primaryLabel="Continue to workflow"
          secondaryLabel="Open context artifact"
          task={{
            ...activeTask,
            nextAction: "Validate context, guardrails, and decisions before dispatching the next packet.",
          }}
        />
      ) : null}

      <div className="content-grid content-grid--context">
        <section className="surface surface--brand">
          <div className="surface__head">
            <div>
              <p className="eyebrow">Canonical brief</p>
              <h3>Context document</h3>
              <p className="muted">Readable source of truth first. Structured fields support it, not replace it.</p>
            </div>
          </div>
          <DocView
            idPrefix="context-brief"
            sections={data.contextDocument}
            summary="A readable brief that keeps intent, guardrails, and next actions visible to the operator."
            title="AI Japan Project Context"
          />
        </section>

        <div className="cp-stack">
          <ActionPanel eyebrow="Structured state" title="Fields that drive the workflow">
            {data.contextFields.map((field) => (
              <div className="signal-row signal-row--compact" key={field.label}>
                <span>{field.label}</span>
                <strong>{field.value}</strong>
              </div>
            ))}
          </ActionPanel>

          <TimelinePanel
            eyebrow="Decision log"
            items={data.decisions.map((decision) => ({
              detail: decision.reason,
              time: decision.date,
              title: decision.title,
            }))}
            title="Why the system is shaped this way"
          />
        </div>
      </div>
    </div>
  );
}
