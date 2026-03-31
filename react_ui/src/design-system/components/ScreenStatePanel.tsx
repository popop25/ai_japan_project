import { ReactNode } from "react";

import { PrototypeScreenState } from "../../types";
import { Panel } from "./Panel";
import { StatusBadge } from "./StatusBadge";

type NonReadyState = Exclude<PrototypeScreenState, "ready">;

const STATE_META: Record<NonReadyState, { badgeLabel: string; badgeStatus: string; tone: "default" | "brand" | "warning" }> = {
  loading: {
    badgeLabel: "Loading",
    badgeStatus: "in_progress",
    tone: "brand",
  },
  error: {
    badgeLabel: "Needs attention",
    badgeStatus: "degraded",
    tone: "warning",
  },
  empty: {
    badgeLabel: "Empty",
    badgeStatus: "pending",
    tone: "default",
  },
};

interface ScreenStatePanelProps {
  state: NonReadyState;
  eyebrow: string;
  title: string;
  description: string;
  detail: string;
  highlights?: string[];
  actions?: ReactNode;
}

export function ScreenStatePanel({ state, eyebrow, title, description, detail, highlights, actions }: ScreenStatePanelProps) {
  const meta = STATE_META[state];

  return (
    <Panel
      actions={actions}
      badge={<StatusBadge label={meta.badgeLabel} status={meta.badgeStatus} />}
      description={description}
      eyebrow={eyebrow}
      title={title}
      tone={meta.tone}
    >
      <div className="surface-state">
        <p className="lead surface-state__summary">{detail}</p>
        {state === "loading" ? (
          <div aria-hidden="true" className="surface-skeleton">
            <span className="surface-skeleton__line surface-skeleton__line--long" />
            <span className="surface-skeleton__line surface-skeleton__line--medium" />
            <span className="surface-skeleton__line surface-skeleton__line--short" />
          </div>
        ) : null}
        {highlights?.length ? (
          <ul className="clean-list">
            {highlights.map((highlight) => (
              <li key={highlight}>{highlight}</li>
            ))}
          </ul>
        ) : null}
      </div>
    </Panel>
  );
}
