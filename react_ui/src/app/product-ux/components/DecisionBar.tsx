import { TaskRecord } from "../types";

interface DecisionBarProps {
  task: TaskRecord;
}

export function DecisionBar({ task }: DecisionBarProps) {
  return (
    <section className="decision-bar">
      {task.decisions.map((decision) => (
        <article key={decision.id} className={`decision-pill is-${decision.state}`}>
          <strong>{decision.label}</strong>
          <span>{decision.rationale}</span>
        </article>
      ))}
    </section>
  );
}

