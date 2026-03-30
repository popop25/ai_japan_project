import { ProductData, ViewId } from "../../types";
import { Panel } from "../../design-system/components/Panel";
import { StatusBadge } from "../../design-system/components/StatusBadge";
import { Stepper } from "../../design-system/components/Stepper";

interface WorkflowWorkspaceScreenProps {
  data: ProductData;
  onNavigate: (view: ViewId) => void;
}

export function WorkflowWorkspaceScreen({ data, onNavigate }: WorkflowWorkspaceScreenProps) {
  const currentStep = data.workflow.steps.find((step) => step.status === "current") ?? data.workflow.steps[data.workflow.steps.length - 1];

  return (
    <>
      <Panel
        tone="warning"
        eyebrow="Workflow workspace"
        title={currentStep.title}
        description={data.workflow.headline}
        badge={<StatusBadge status={data.workflow.currentStatus} />}
      >
        <div className="split-callout">
          <div className="callout-copy">
            <p className="lead">{currentStep.detail}</p>
            <p className="footer-note">Operator action: {currentStep.operatorAction}</p>
            <p className="footer-note">Outcome after completion: {currentStep.outcome}</p>
          </div>
          <div className="button-stack">
            <button className="button button--primary" onClick={() => onNavigate("artifacts")} type="button">
              Inspect blocking artifact
            </button>
            <button className="button button--secondary" onClick={() => onNavigate("dashboard")} type="button">
              Back to dashboard
            </button>
          </div>
        </div>
      </Panel>

      <Panel
        eyebrow="Guided flow"
        title={data.workflow.title}
        description={data.workflow.subtitle}
        badge={<StatusBadge status={data.workflow.currentStatus} />}
      >
        <Stepper steps={data.workflow.steps} />
      </Panel>

      <div className="screen-grid screen-grid--workflow-main">
        <Panel
          eyebrow="Packet contract"
          title="Packet preview"
          description="The frontend should render the packet contract clearly before the handoff leaves the product."
        >
          <div className="detail-grid">
            <div className="detail-tile">
              <span>Audience</span>
              <strong>{data.workflow.packet.audience}</strong>
            </div>
            <div className="detail-tile">
              <span>Handoff mode</span>
              <strong>{data.workflow.packet.handoffMode}</strong>
            </div>
            <div className="detail-tile">
              <span>Objective</span>
              <strong>{data.workflow.packet.objective}</strong>
            </div>
          </div>

          <div className="list-columns">
            <div>
              <h4>Inputs</h4>
              <ul className="clean-list">
                {data.workflow.packet.inputs.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4>Output contract</h4>
              <ul className="clean-list">
                {data.workflow.packet.outputContract.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>

          <pre className="packet-snippet">{data.workflow.packet.snippet}</pre>
        </Panel>

        <div className="stack">
          <Panel
            eyebrow="Handoff"
            title="Supported operator paths"
            description="The product should meet the operator where they already work instead of forcing one agent surface."
          >
            {data.workflow.handoffModes.map((mode) => (
              <div className="handoff-card" key={mode.name}>
                <h3>{mode.name}</h3>
                <p>{mode.summary}</p>
                <strong>{mode.fit}</strong>
              </div>
            ))}
          </Panel>

          <Panel
            eyebrow="Traceability"
            title="Run trace"
            description="A productized history of what the harness already recorded behind the scenes."
          >
            <div className="timeline">
              {data.workflow.runTrace.map((entry) => (
                <div className="timeline__item" key={`${entry.time}-${entry.label}`}>
                  <span className="timeline__time">{entry.time}</span>
                  <div className="timeline__body">
                    <h3>{entry.label}</h3>
                    <p>{entry.detail}</p>
                  </div>
                  <StatusBadge status={entry.status} />
                </div>
              ))}
            </div>
          </Panel>
        </div>
      </div>

      <div className="screen-grid screen-grid--two-column">
        <Panel
          eyebrow="Operator checklist"
          title="What the user should do next"
          description="Keep the human-in-the-loop explicit and make the sequence easy to follow."
        >
          <div className="stack">
            {data.workflow.checklists.map((block) => (
              <div className="field-row" key={block.title}>
                <span className="field-label">{block.title}</span>
                <ul className="clean-list">
                  {block.items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Panel>

        <Panel
          eyebrow="Downstream sync"
          title="What happens after approval"
          description="Future React clients should request these outcomes from the backend instead of deriving them locally."
        >
          <div className="sync-list">
            {data.workflow.syncPreview.map((item) => (
              <div className="sync-item" key={item.label}>
                <div>
                  <h3>{item.label}</h3>
                  <span>{item.target}</span>
                  <p>{item.detail}</p>
                </div>
                <StatusBadge status={item.status} />
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </>
  );
}
