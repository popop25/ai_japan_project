import { useMemo, useState } from "react";

import { ProductData, ViewId } from "../../types";
import { DocView } from "../../design-system/components/DocView";
import { Panel } from "../../design-system/components/Panel";
import { StatusBadge } from "../../design-system/components/StatusBadge";
import { cx } from "../../utils";

interface ArtifactViewerScreenProps {
  data: ProductData;
  onNavigate: (view: ViewId) => void;
}

export function ArtifactViewerScreen({ data, onNavigate }: ArtifactViewerScreenProps) {
  const [selectedArtifactId, setSelectedArtifactId] = useState(data.artifacts[0]?.id ?? "");

  const selectedArtifact = useMemo(
    () => data.artifacts.find((artifact) => artifact.id === selectedArtifactId) ?? data.artifacts[0],
    [data.artifacts, selectedArtifactId],
  );

  const tone =
    selectedArtifact.kind === "critic_review"
      ? "warning"
      : selectedArtifact.kind === "context_snapshot"
        ? "success"
        : "brand";

  return (
    <>
      <Panel
        tone={tone}
        eyebrow="Artifact viewer"
        title="Summary-first artifact review"
        description={selectedArtifact.summary}
        badge={<StatusBadge status={selectedArtifact.status} />}
      >
        <div className="artifact-selector">
          {data.artifacts.map((artifact) => (
            <button
              className={cx(
                "artifact-selector__button",
                artifact.id === selectedArtifact.id && "artifact-selector__button--active",
              )}
              key={artifact.id}
              onClick={() => setSelectedArtifactId(artifact.id)}
              type="button"
            >
              <strong>{artifact.title}</strong>
              <span>
                {artifact.linkedTask} 쨌 {artifact.updatedAt}
              </span>
            </button>
          ))}
        </div>
      </Panel>

      <div className="screen-grid screen-grid--two-column">
        <Panel
          eyebrow="Selected artifact"
          title={selectedArtifact.title}
          description="Traceability and readable summary should come before raw markdown."
          badge={
            selectedArtifact.verdict ? (
              <StatusBadge
                label={selectedArtifact.verdict === "revise" ? "Critic says revise" : "Critic approved"}
                status={selectedArtifact.verdict === "revise" ? "revision_needed" : "review_requested"}
              />
            ) : (
              <StatusBadge status={selectedArtifact.status} />
            )
          }
        >
          <div className="detail-grid">
            <div className="detail-tile">
              <span>Kind</span>
              <strong>{selectedArtifact.kind.replace("_", " ")}</strong>
            </div>
            <div className="detail-tile">
              <span>Updated</span>
              <strong>{selectedArtifact.updatedAt}</strong>
            </div>
            <div className="detail-tile">
              <span>Linked task</span>
              <strong>{selectedArtifact.linkedTask}</strong>
            </div>
          </div>

          <div className="artifact-card__links">
            {selectedArtifact.externalLinks.map((link) => (
              <a className="link-pill" href={link.href} key={`${selectedArtifact.id}-${link.label}`} rel="noreferrer" target="_blank">
                {link.label}
                <span>{link.system}</span>
              </a>
            ))}
          </div>
        </Panel>

        <Panel
          eyebrow="Operator readout"
          title="What changes because of this artifact"
          description="The viewer should help the operator decide what to do next, not just display the file."
        >
          <div className="callout-list">
            {selectedArtifact.callouts.map((callout) => (
              <div className="callout" key={callout}>
                {callout}
              </div>
            ))}
          </div>
          <div className="button-stack button-stack--horizontal">
            <button className="button button--primary" onClick={() => onNavigate("workflow")} type="button">
              Open linked workflow
            </button>
            <button className="button button--secondary" onClick={() => onNavigate("context")} type="button">
              Check source context
            </button>
          </div>
        </Panel>
      </div>

      <Panel
        eyebrow="Document anatomy"
        title="Readable narrative plus structured detail"
        description="The same component can render context pages, PM drafts, and Critic reviews without turning them into raw file dumps."
      >
        <DocView sections={selectedArtifact.sections} summary={selectedArtifact.summary} title={selectedArtifact.title} />
      </Panel>
    </>
  );
}
