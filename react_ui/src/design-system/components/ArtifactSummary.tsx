import { ArtifactItem } from "../../types";
import { StatusBadge } from "./StatusBadge";

interface ArtifactSummaryProps {
  artifact: ArtifactItem;
  title?: string;
}

export function ArtifactSummary({ artifact, title }: ArtifactSummaryProps) {
  return (
    <section className="artifact-summary">
      <div className="artifact-summary__head">
        <div>
          <p className="eyebrow">Artifact summary</p>
          <h3>{title ?? artifact.title}</h3>
        </div>
        <StatusBadge
          label={artifact.verdict ? `Verdict: ${artifact.verdict}` : undefined}
          status={artifact.verdict === "revise" ? "revision_needed" : artifact.status}
        />
      </div>

      <div className="artifact-summary__lede">
        <p>{artifact.summary}</p>
      </div>

      <div className="artifact-summary__meta">
        <div>
          <span>Source</span>
          <strong>{artifact.kind.replace(/_/g, " ")}</strong>
        </div>
        <div>
          <span>Linked task</span>
          <strong>{artifact.linkedTask}</strong>
        </div>
        <div>
          <span>Updated</span>
          <strong>{artifact.updatedAt}</strong>
        </div>
      </div>

      <div className="artifact-summary__callouts">
        {artifact.callouts.map((callout) => (
          <div className="artifact-summary__callout" key={callout}>
            {callout}
          </div>
        ))}
      </div>
    </section>
  );
}
