import { DocumentSection } from "../../types";

interface DocViewProps {
  title: string;
  summary: string;
  sections: DocumentSection[];
}

export function DocView({ title, summary, sections }: DocViewProps) {
  return (
    <div className="doc-view">
      <aside className="doc-view__outline">
        <p className="eyebrow eyebrow--muted">Document outline</p>
        <h3>{title}</h3>
        <p className="doc-view__summary">{summary}</p>
        <ol className="doc-view__outline-list">
          {sections.map((section) => (
            <li key={section.id}>
              <a href={`#${section.id}`}>{section.title}</a>
            </li>
          ))}
        </ol>
      </aside>
      <div className="doc-view__content">
        {sections.map((section) => (
          <section className="doc-view__section" id={section.id} key={section.id}>
            <div className="doc-view__section-head">
              <h4>{section.title}</h4>
              <p>{section.summary}</p>
            </div>
            {section.paragraphs.map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
            {section.bullets?.length ? (
              <ul className="doc-view__bullets">
                {section.bullets.map((bullet) => (
                  <li key={bullet}>{bullet}</li>
                ))}
              </ul>
            ) : null}
          </section>
        ))}
      </div>
    </div>
  );
}
