import { WorkflowStep } from "../../types";
import { cx } from "../../utils";

interface StepperProps {
  steps: WorkflowStep[];
}

export function Stepper({ steps }: StepperProps) {
  return (
    <ol className="stepper">
      {steps.map((step, index) => (
        <li className={cx("stepper__item", `stepper__item--${step.status}`)} key={step.id}>
          <div className="stepper__marker">{index + 1}</div>
          <div className="stepper__content">
            <div className="stepper__topline">
              <h3>{step.title}</h3>
              <span className="stepper__status">{step.status}</span>
            </div>
            <p className="stepper__detail">{step.detail}</p>
            <dl className="stepper__meta">
              <div>
                <dt>Operator action</dt>
                <dd>{step.operatorAction}</dd>
              </div>
              <div>
                <dt>Outcome</dt>
                <dd>{step.outcome}</dd>
              </div>
            </dl>
          </div>
        </li>
      ))}
    </ol>
  );
}
