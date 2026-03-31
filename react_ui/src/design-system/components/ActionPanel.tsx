import { ReactNode } from "react";

interface ActionPanelProps {
  eyebrow: string;
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  tone?: "default" | "brand" | "warning";
}

export function ActionPanel({ eyebrow, title, description, actions, children, tone = "default" }: ActionPanelProps) {
  return (
    <section className={`surface surface--${tone}`}>
      <div className="surface__head">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h3>{title}</h3>
          {description ? <p className="muted">{description}</p> : null}
        </div>
        {actions ? <div className="surface__actions">{actions}</div> : null}
      </div>
      <div className="cp-stack">{children}</div>
    </section>
  );
}
