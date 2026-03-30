import { ReactNode } from "react";

import { cx } from "../../utils";

interface PanelProps {
  eyebrow?: string;
  title?: string;
  description?: string;
  badge?: ReactNode;
  actions?: ReactNode;
  tone?: "default" | "brand" | "success" | "warning" | "critical";
  className?: string;
  children: ReactNode;
}

export function Panel({
  eyebrow,
  title,
  description,
  badge,
  actions,
  tone = "default",
  className,
  children,
}: PanelProps) {
  return (
    <section className={cx("panel", tone !== "default" && `panel--${tone}`, className)}>
      {(eyebrow || title || description || badge || actions) && (
        <header className="panel__header">
          <div>
            {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
            {title ? <h2 className="panel__title">{title}</h2> : null}
            {description ? <p className="panel__description">{description}</p> : null}
          </div>
          {(badge || actions) && (
            <div className="panel__meta">
              {badge}
              {actions}
            </div>
          )}
        </header>
      )}
      <div className="panel__body">{children}</div>
    </section>
  );
}
