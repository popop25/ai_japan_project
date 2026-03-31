import { useEffect, useState } from "react";

import { ProductData, PrototypeScreenState, ViewId } from "../../types";
import { ArtifactSummary } from "../../design-system/components/ArtifactSummary";
import { FocusBar } from "../../design-system/components/FocusBar";
import { DocView } from "../../design-system/components/DocView";
import { InlineNotice } from "../../design-system/components/InlineNotice";
import { ProofPanel } from "../../design-system/components/ProofPanel";
import { ScreenStatePanel } from "../../design-system/components/ScreenStatePanel";
import { cx } from "../../utils";

interface ArtifactViewerScreenProps {
  data: ProductData;
  onNavigate: (view: ViewId) => void;
  state?: PrototypeScreenState;
  onResetState?: () => void;
}

function recoverFixture(onResetState?: () => void) {
  if (onResetState) {
    onResetState();
    return;
  }

  if (typeof window !== "undefined") {
    window.location.reload();
  }
}

export function ArtifactViewerScreen({ data, onNavigate, state = "ready", onResetState }: ArtifactViewerScreenProps) {
  const [selectedArtifactId, setSelectedArtifactId] = useState(data.artifacts[0]?.id ?? "");

  useEffect(() => {
    if (!data.artifacts.length) {
      if (selectedArtifactId) {
        setSelectedArtifactId("");
      }
      return;
    }

    if (!data.artifacts.some((artifact) => artifact.id === selectedArtifactId)) {
      setSelectedArtifactId(data.artifacts[0].id);
    }
  }, [data.artifacts, selectedArtifactId]);

  if (state === "loading") {
    return (
      <ScreenStatePanel
        description="Artifact metadata and rendered body are still loading."
        detail="Keep verdict, summary, and source slots stable while the future artifact endpoint swaps in live data."
        eyebrow="Artifact Review"
        highlights={[
          "Verdict and source should load before long document content if needed.",
          "Do not reconstruct Critic frontmatter in the client.",
        ]}
        title="Loading artifact review"
        state="loading"
      />
    );
  }

  if (state === "error") {
    return (
      <ScreenStatePanel
        actions={
          <div className="button-row">
            <button className="button button--primary" onClick={() => recoverFixture(onResetState)} type="button">
              Use fixture payload
            </button>
            <button className="button button--secondary" onClick={() => onNavigate("workflow")} type="button">
              Open workflow detail
            </button>
          </div>
        }
        description="The selected artifact could not be rendered safely."
        detail="Keep the shell responsive and wait for a canonical artifact payload from the backend."
        eyebrow="Artifact Review"
        highlights={[
          "Artifact parsing remains a backend concern.",
          "The React client should never reconstruct review metadata on its own.",
        ]}
        title="Artifact review unavailable"
        state="error"
      />
    );
  }

  const selectedArtifact = data.artifacts.find((artifact) => artifact.id === selectedArtifactId) ?? data.artifacts[0] ?? null;

  if (state === "empty" || selectedArtifact === null) {
    return (
      <ScreenStatePanel
        actions={
          <div className="button-row">
            <button className="button button--primary" onClick={() => onNavigate("workflow")} type="button">
              Open workflow detail
            </button>
            <button className="button button--secondary" onClick={() => onNavigate("context")} type="button">
              Review context
            </button>
          </div>
        }
        description="There are no reviewable artifacts yet."
        detail="The viewer should guide the operator back to workflow or context when live payloads have not produced a readable draft or review."
        eyebrow="Artifact Review"
        highlights={[
          "No artifacts should render an intentional empty state.",
          "Document body stays secondary until a real artifact exists.",
        ]}
        title="No artifacts available"
        state="empty"
      />
    );
  }

  const tone = selectedArtifact.kind === "critic_review" ? "warning" : selectedArtifact.kind === "context_snapshot" ? "default" : "brand";
  const linkedTask = data.queue.find((item) => item.jiraKey === selectedArtifact.linkedTask) ?? data.queue[0] ?? null;

  return (
    <div className="cp-stack cp-stack--xl">
      {linkedTask ? (
        <FocusBar
          currentStage={linkedTask.stage}
          onPrimaryAction={() => onNavigate("workflow")}
          onSecondaryAction={() => onNavigate("context")}
          primaryLabel="Open linked workflow"
          secondaryLabel="Check source context"
          task={linkedTask}
        />
      ) : null}

      <div className="content-grid content-grid--artifact">
        <ArtifactSummary artifact={selectedArtifact} title="Verdict / summary / source" />
        {linkedTask ? <ProofPanel artifact={selectedArtifact} connections={data.connections} task={linkedTask} /> : null}
      </div>

      <section className="surface surface--brand">
        <div className="surface__head">
          <div>
            <p className="eyebrow">Artifact switcher</p>
            <h3>Available review targets</h3>
            <p className="muted">Fixture-backed list. It does not imply a live multi-artifact backend session.</p>
          </div>
        </div>
        <div className="artifact-switcher">
          {data.artifacts.map((artifact) => (
            <button
              className={cx("artifact-switcher__item", artifact.id === selectedArtifact.id && "artifact-switcher__item--active")}
              key={artifact.id}
              onClick={() => setSelectedArtifactId(artifact.id)}
              type="button"
            >
              <strong>{artifact.title}</strong>
              <span>
                {artifact.linkedTask} ¡¤ {artifact.updatedAt}
              </span>
            </button>
          ))}
        </div>
      </section>

      <section className={`surface ${tone === "default" ? "" : `surface--${tone}`}`.trim()}>
        <div className="surface__head">
          <div>
            <p className="eyebrow">Doc view</p>
            <h3>Rendered body</h3>
            <p className="muted">The body is intentionally secondary to verdict, summary, and source traceability.</p>
          </div>
        </div>
        <DocView
          idPrefix={`artifact-${selectedArtifact.id}`}
          sections={selectedArtifact.sections}
          summary={selectedArtifact.summary}
          title={selectedArtifact.title}
        />
      </section>
    </div>
  );
}
