import { ReactNode } from "react";

import { StatusBadge } from "./StatusBadge";

interface TimelineItem {
  time: string;
  title: string;
  detail: string;
  status?: string;
  aside?: ReactNode;
}

interface TimelinePanelProps {
  eyebrow: string;
  title: string;
  items: TimelineItem[];
}

export function TimelinePanel({ eyebrow, title, items }: TimelinePanelProps) {
  return (
    <section className="surface">
      <div className="surface__head">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h3>{title}</h3>
        </div>
      </div>
      <div className="timeline-panel">
        {items.map((item) => (
          <article className="timeline-panel__item" key={`${item.time}-${item.title}`}>
            <span className="timeline-panel__time">{item.time}</span>
            <div className="timeline-panel__body">
              <h4>{item.title}</h4>
              <p>{item.detail}</p>
            </div>
            {item.aside ?? (item.status ? <StatusBadge status={item.status} /> : null)}
          </article>
        ))}
      </div>
    </section>
  );
}
