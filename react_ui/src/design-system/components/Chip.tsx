import { cx } from "../../utils";

interface ChipProps {
  label: string;
  tone?: "neutral" | "brand" | "success" | "warning";
  className?: string;
}

export function Chip({ label, tone = "neutral", className }: ChipProps) {
  return <span className={cx("chip", `chip--${tone}`, className)}>{label}</span>;
}
