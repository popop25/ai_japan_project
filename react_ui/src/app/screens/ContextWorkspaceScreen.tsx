import { ProductData, ViewId } from "../../types";
import { DocView } from "../../design-system/components/DocView";
import { Panel } from "../../design-system/components/Panel";

interface ContextWorkspaceScreenProps {
  data: ProductData;
  onNavigate: (view: ViewId) => void;
}

export function ContextWorkspaceScreen({ data, onNavigate }: ContextWorkspaceScreenProps) {
  return (
    <>
      <Panel
        tone="brand"
        eyebrow="Context workspace"
        title="Make the brief readable enough to run the workflow from it."
        description="Narrative context and structured state live together so the operator can understand why the workflow exists, not just what fields are filled in."
      >
        <div className="split-callout">
          <div className="callout-copy">
            <p className="lead">
              This surface borrows document readability from modern work tools while keeping the control-plane contract explicit.
            </p>
            <p className="footer-note">
              The context should feel like a living operating brief that explains purpose, audience, guardrails, and next actions in one place.
            </p>
          </div>
          <div className="button-stack">
            <button className="button button--primary" onClick={() => onNavigate("workflow")} type="button">
              Continue to workflow
            </button>
            <button className="button button--secondary" onClick={() => onNavigate("artifacts")} type="button">
              Review context snapshot
            </button>
          </div>
        </div>
      </Panel>

      <div className="screen-grid screen-grid--context">
        <Panel
          eyebrow="Canonical brief"
          title="Context document"
          description="The product should render the narrative source of truth directly rather than burying it behind forms."
        >
          <DocView
            sections={data.contextDocument}
            summary="A readable brief that keeps intent, guardrails, and next actions visible to the operator."
            title="AI Japan Project Context"
          />
        </Panel>

        <div className="stack">
          <Panel
            eyebrow="Structured state"
            title="Project fields"
            description="These fields stay important, but they should support the story instead of replacing it."
          >
            <div className="field-list">
              {data.contextFields.map((field) => (
                <div className="field-row" key={field.label}>
                  <span className="field-label">{field.label}</span>
                  <p className="field-value">{field.value}</p>
                </div>
              ))}
            </div>
          </Panel>

          <Panel
            eyebrow="Decision log"
            title="Why the program is shaped this way"
            description="Explicit decisions keep the context workspace useful for both new operators and future reviewers."
          >
            <div className="timeline timeline--compact">
              {data.decisions.map((decision) => (
                <div className="timeline__item" key={`${decision.date}-${decision.title}`}>
                  <span className="timeline__time">{decision.date}</span>
                  <div className="timeline__body">
                    <h3>{decision.title}</h3>
                    <p>{decision.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel
            eyebrow="Operating posture"
            title="What this UI is optimizing for"
            description="The React surface should feel calm and productized without turning the workflow into a developer-only tool."
          >
            <div className="callout-list">
              <div className="callout">Keep context editable and readable in the same view.</div>
              <div className="callout">Show workflow implications before low-level metadata.</div>
              <div className="callout">Treat external agent handoff as part of the core product, not a workaround.</div>
            </div>
          </Panel>
        </div>
      </div>
    </>
  );
}
