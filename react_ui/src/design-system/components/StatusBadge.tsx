import { cx } from "../../utils";

const STATUS_META: Record<string, { label: string; tone: string }> = {
  pending: { label: "Pending", tone: "neutral" },
  in_progress: { label: "In progress", tone: "brand" },
  review_requested: { label: "Ready for review", tone: "positive" },
  revision_needed: { label: "Needs revision", tone: "warning" },
  done: { label: "Done", tone: "positive" },
  connected: { label: "Connected", tone: "positive" },
  degraded: { label: "Attention", tone: "warning" },
  current: { label: "Current step", tone: "brand" },
};

function formatLabel(status: string): string {
  return status
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

interface StatusBadgeProps {
  status: string;
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const meta = STATUS_META[status] ?? { label: formatLabel(status), tone: "neutral" };

  return (
    <span className={cx("status-badge", `status-badge--${meta.tone}`, className)}>
      <span className="status-badge__dot" aria-hidden="true" />
      {label ?? meta.label}
    </span>
  );
}
