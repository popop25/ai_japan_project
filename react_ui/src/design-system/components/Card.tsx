import { ReactNode } from "react";

import { cx } from "../../utils";

interface CardProps {
  eyebrow?: string;
  title: string;
  badge?: ReactNode;
  className?: string;
  children: ReactNode;
}

export function Card({ eyebrow, title, badge, className, children }: CardProps) {
  return (
    <article className={cx("card", className)}>
      <header className="card__header">
        <div>
          {eyebrow ? <p className="eyebrow eyebrow--muted">{eyebrow}</p> : null}
          <h3 className="card__title">{title}</h3>
        </div>
        {badge}
      </header>
      <div className="card__body">{children}</div>
    </article>
  );
}
