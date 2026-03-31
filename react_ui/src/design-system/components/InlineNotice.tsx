import { cx } from "../../utils";

interface InlineNoticeProps {
  title: string;
  description: string;
  tone?: "default" | "brand" | "warning" | "success";
}

export function InlineNotice({ title, description, tone = "default" }: InlineNoticeProps) {
  return (
    <div className={cx("inline-notice", tone !== "default" && `inline-notice--${tone}`)}>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}
