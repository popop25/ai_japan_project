import { useId } from "react";

import { DocumentSection } from "../../types";

interface DocViewProps {
  title: string;
  summary: string;
  sections: DocumentSection[];
  idPrefix?: string;
}

function sanitizeId(value: string): string {
  const sanitized = value.toLowerCase().replace(/[^a-z0-9_-]+/g, "-").replace(/^-+|-+$/g, "");
  return sanitized || "doc";
}

export function DocView({ title, summary, sections, idPrefix }: DocViewProps) {
  const generatedId = useId();
  const baseId = sanitizeId(idPrefix ?? generatedId);

  const scrollToSection = (sectionId: string) => {
    if (typeof document === "undefined") {
      return;
    }

    document.getElementById(`${baseId}-${sectionId}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="doc-frame">
      <aside className="doc-frame__outline">
        <p className="eyebrow eyebrow--muted">Doc view</p>
        <h3>{title}</h3>
        <p className="muted">{summary}</p>
        {sections.length ? (
          <ol className="doc-frame__outline-list">
            {sections.map((section) => (
              <li key={section.id}>
                <button className="doc-frame__outline-link" onClick={() => scrollToSection(section.id)} type="button">
                  {section.title}
                </button>
              </li>
            ))}
          </ol>
        ) : (
          <p className="muted">Outline appears after the backend returns rendered sections.</p>
        )}
      </aside>
      <div className="doc-frame__content">
        {sections.length ? (
          sections.map((section) => (
            <section className="doc-frame__section" id={`${baseId}-${section.id}`} key={section.id}>
              <div className="doc-frame__section-head">
                <h4>{section.title}</h4>
                <p>{section.summary}</p>
              </div>
              {section.paragraphs.map((paragraph) => (
                <p key={paragraph}>{paragraph}</p>
              ))}
              {section.bullets?.length ? (
                <ul className="doc-frame__bullets">
                  {section.bullets.map((bullet) => (
                    <li key={bullet}>{bullet}</li>
                  ))}
                </ul>
              ) : null}
            </section>
          ))
        ) : (
          <div className="doc-frame__empty">
            <h4>No document sections yet</h4>
            <p>The surface stays stable when an artifact exists but the readable document body has not been delivered.</p>
          </div>
        )}
      </div>
    </div>
  );
}
