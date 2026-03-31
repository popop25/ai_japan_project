import { ArtifactItem, Connection, QueueItem } from "../../types";
import { StatusBadge } from "./StatusBadge";

interface ProofPanelProps {
  task: QueueItem;
  artifact?: ArtifactItem | null;
  connections: Connection[];
  title?: string;
}

export function ProofPanel({ task, artifact, connections, title = "Traceability proof" }: ProofPanelProps) {
  const jiraLink = artifact?.externalLinks.find((link) => link.system === "Jira");
  const confluenceLinks = artifact?.externalLinks.filter((link) => link.system === "Confluence") ?? [];

  return (
    <section className="proof-panel">
      <div className="proof-panel__head">
        <div>
          <p className="eyebrow">Proof panel</p>
          <h3>{title}</h3>
        </div>
        <StatusBadge status={artifact?.status ?? task.status} />
      </div>

      <div className="proof-panel__summary">
        <div>
          <span>Jira</span>
          <strong>{jiraLink?.label ?? task.jiraKey}</strong>
        </div>
        <div>
          <span>Confluence</span>
          <strong>{confluenceLinks.length ? `${confluenceLinks.length} linked pages` : "Pending publish"}</strong>
        </div>
        <div>
          <span>Verdict</span>
          <strong>{artifact?.verdict ? artifact.verdict.toUpperCase() : "Operational draft"}</strong>
        </div>
      </div>

      <div className="proof-panel__links">
        {artifact?.externalLinks.length ? (
          artifact.externalLinks.map((link) => (
            <a className="proof-link" href={link.href} key={`${artifact.id}-${link.label}`} rel="noreferrer" target="_blank">
              <span>{link.system}</span>
              <strong>{link.label}</strong>
            </a>
          ))
        ) : (
          <div className="proof-link proof-link--muted">
            <span>Fixture note</span>
            <strong>Links appear when canonical references are supplied by the backend.</strong>
          </div>
        )}
      </div>

      <div className="proof-panel__systems">
        {connections.map((connection) => (
          <div className="proof-system" key={connection.id}>
            <div>
              <strong>{connection.name}</strong>
              <p>{connection.description}</p>
            </div>
            <StatusBadge status={connection.status} />
          </div>
        ))}
      </div>
    </section>
  );
}
