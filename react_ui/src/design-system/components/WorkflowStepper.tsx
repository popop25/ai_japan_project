import { WorkflowStep } from "../../types";
import { cx } from "../../utils";

interface WorkflowStepperProps {
  steps: WorkflowStep[];
}

export function WorkflowStepper({ steps }: WorkflowStepperProps) {
  return (
    <section className="surface surface--flush">
      <div className="surface__head">
        <div>
          <p className="eyebrow">Workflow stepper</p>
          <h3>State machine</h3>
        </div>
      </div>
      <ol className="workflow-stepper">
        {steps.map((step, index) => (
          <li className={cx("workflow-stepper__item", `workflow-stepper__item--${step.status}`)} key={step.id}>
            <div className="workflow-stepper__rail">
              <span className="workflow-stepper__index">{String(index + 1).padStart(2, "0")}</span>
              <span className="workflow-stepper__line" aria-hidden="true" />
            </div>
            <div className="workflow-stepper__body">
              <div className="workflow-stepper__top">
                <div>
                  <span className="workflow-stepper__state">{step.status}</span>
                  <h4>{step.title}</h4>
                </div>
              </div>
              <p>{step.detail}</p>
              <div className="workflow-stepper__meta">
                <div>
                  <span>Operator action</span>
                  <strong>{step.operatorAction}</strong>
                </div>
                <div>
                  <span>State output</span>
                  <strong>{step.outcome}</strong>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
