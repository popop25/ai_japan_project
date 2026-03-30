import { ProductData, ViewId } from "../../types";
import { Card } from "../../design-system/components/Card";
import { Panel } from "../../design-system/components/Panel";
import { StatusBadge } from "../../design-system/components/StatusBadge";

interface DashboardScreenProps {
  data: ProductData;
  onNavigate: (view: ViewId) => void;
}

function queueActionTarget(status: string): ViewId {
  return status === "review_requested" ? "artifacts" : "workflow";
}

function queueActionLabel(status: string): string {
  return status === "review_requested" ? "Open artifact" : "Continue workflow";
}

export function DashboardScreen({ data, onNavigate }: DashboardScreenProps) {
  const maxScope = Math.max(...data.projectGraph.map((point) => point.scope));

  return (
    <>
      <Panel
        tone="brand"
        eyebrow="Dashboard"
        title="Run AI work like an operating system, not a chat log."
        description="The first read should tell an operator what is happening, what requires a decision, and which systems are already in sync."
      >
        <div className="split-callout">
          <div className="callout-copy">
            <p className="lead">{data.overview.nextActionTitle}</p>
            <p className="footer-note">{data.overview.nextActionBody}</p>
          </div>
          <div className="button-stack">
            <button className="button button--primary" onClick={() => onNavigate("workflow")} type="button">
              Open workflow workspace
            </button>
            <button className="button button--secondary" onClick={() => onNavigate("artifacts")} type="button">
              Review latest artifact
            </button>
          </div>
        </div>
      </Panel>

      <div className="metric-grid">
        {data.metrics.map((metric) => (
          <Card className="metric-card" key={metric.label} title={metric.label}>
            <div className="card__value">{metric.value}</div>
            <p>{metric.detail}</p>
          </Card>
        ))}
      </div>

      <div className="screen-grid screen-grid--dashboard-top">
        <Panel
          eyebrow="Work queue"
          title="Operational queue"
          description="Keep the operator focused on the next meaningful action instead of the raw task ledger."
        >
          <div className="queue-list">
            {data.queue.map((item) => (
              <article className="queue-item" key={item.id}>
                <div className="queue-item__head">
                  <div>
                    <p className="queue-item__eyebrow">
                      {item.jiraKey} 쨌 {item.stage}
                    </p>
                    <h3>{item.title}</h3>
                  </div>
                  <StatusBadge status={item.status} />
                </div>
                <div className="queue-item__meta">
                  <span>Owner: {item.owner}</span>
                  <span>Updated: {item.updatedAt}</span>
                  <span>{item.artifactCount} artifacts</span>
                </div>
                <p>{item.nextAction}</p>
                <button
                  className="button button--secondary"
                  onClick={() => onNavigate(queueActionTarget(item.status))}
                  type="button"
                >
                  {queueActionLabel(item.status)}
                </button>
              </article>
            ))}
          </div>
        </Panel>

        <div className="stack">
          <Panel
            eyebrow="Project graph"
            title="Progress signal"
            description="Scope, started work, and completed work should read in one glance so the queue feels grounded in program momentum."
          >
            <div className="graph__legend">
              <span className="legend-pill">
                <span className="legend-swatch legend-swatch--scope" />
                Scope
              </span>
              <span className="legend-pill">
                <span className="legend-swatch legend-swatch--started" />
                Started
              </span>
              <span className="legend-pill">
                <span className="legend-swatch legend-swatch--completed" />
                Completed
              </span>
            </div>
            <div className="graph">
              {data.projectGraph.map((point) => (
                <div className="graph-row" key={point.label}>
                  <span className="graph-row__label">{point.label}</span>
                  <div className="graph-row__bars">
                    <div className="graph-bar graph-bar--scope">
                      <span style={{ width: `${(point.scope / maxScope) * 100}%` }} />
                    </div>
                    <div className="graph-bar graph-bar--started">
                      <span style={{ width: `${(point.started / maxScope) * 100}%` }} />
                    </div>
                    <div className="graph-bar graph-bar--completed">
                      <span style={{ width: `${(point.completed / maxScope) * 100}%` }} />
                    </div>
                  </div>
                  <span className="graph-row__value">{point.completed} done</span>
                </div>
              ))}
            </div>
          </Panel>

          <Panel
            eyebrow="Connected surface"
            title="Knowledge, execution, and tracking"
            description="The operator should feel Jira, Confluence, and external agents as one operating surface rather than three detached tools."
          >
            <div className="connection-grid">
              {data.connections.map((connection) => (
                <Card badge={<StatusBadge status={connection.status} />} key={connection.id} title={connection.name}>
                  <p>{connection.description}</p>
                  <p className="footer-note">Last signal: {connection.lastSync}</p>
                </Card>
              ))}
            </div>
          </Panel>
        </div>
      </div>

      <div className="screen-grid screen-grid--two-column">
        <Panel
          eyebrow="Latest signals"
          title="Recent activity"
          description="Every event explains what changed and why the operator should care."
        >
          <div className="timeline">
            {data.activity.map((item) => (
              <div className="timeline__item" key={`${item.time}-${item.title}`}>
                <span className="timeline__time">{item.time}</span>
                <div className="timeline__body">
                  <h3>{item.title}</h3>
                  <p>{item.detail}</p>
                </div>
                <StatusBadge status={item.status} />
              </div>
            ))}
          </div>
        </Panel>

        <Panel
          eyebrow="Artifacts"
          title="Latest artifacts"
          description="Summary-first cards make the newest output readable before the user opens full markdown."
        >
          <div className="artifact-list">
            {data.artifacts.map((artifact) => (
              <Card badge={<StatusBadge status={artifact.status} />} key={artifact.id} title={artifact.title}>
                <p>{artifact.summary}</p>
                <div className="artifact-card__links">
                  {artifact.externalLinks.map((link) => (
                    <a className="link-pill" href={link.href} key={`${artifact.id}-${link.label}`} rel="noreferrer" target="_blank">
                      {link.label}
                      <span>{link.system}</span>
                    </a>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </Panel>
      </div>
    </>
  );
}
