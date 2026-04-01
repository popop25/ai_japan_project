import { TaskRecord } from "../types";

interface AgentConnectionPanelProps {
  onContinue: () => void;
  task: TaskRecord;
}

function primaryCtaLabel(task: TaskRecord): string {
  if (task.displayState === "not_started") {
    return "브리프 준비";
  }

  if (task.displayState === "brief_ready") {
    return "전달 열기";
  }

  return task.nextActionLabel;
}

function statusLabel(status: TaskRecord["connectedAgents"][number]["status"]) {
  switch (status) {
    case "connected":
      return "준비";
    case "reviewing":
      return "대기";
    case "waiting":
      return "보류";
    default:
      return status;
  }
}

export function AgentConnectionPanel({ onContinue, task }: AgentConnectionPanelProps) {
  return (
    <div className="aside-stack">
      <section className="aside-section">
        <div className="aside-label">연결된 에이전트</div>
        <div className="agent-list agent-list--compact">
          {task.connectedAgents.map((agent) => (
            <article key={agent.id} className="agent-item">
              <div className="agent-avatar">{agent.roleLabel.replace(" Agent", "").slice(0, 2).toUpperCase()}</div>
              <div className="agent-info">
                <div className="agent-name">{agent.name}</div>
                <span className="agent-role-badge">역할: {agent.roleLabel.replace(" Agent", "")}</span>
              </div>
              <span className="agent-ready">{statusLabel(agent.status)}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="aside-section">
        <div className="aside-label">다음 행동</div>
        <div className="next-action-card">
          <div className="na-header">
            <span className="na-eyebrow">다음 단계</span>
            <span className="na-step-tag">-&gt; 02 에이전트 전달</span>
          </div>
          <div className="na-body">
            <p className="na-text">{task.nextActionDetail}</p>
            <button className="cta-btn" onClick={onContinue} type="button">
              <span>{primaryCtaLabel(task)}</span>
              <span className="cta-arrow">&gt;</span>
            </button>
          </div>
        </div>
      </section>

      <section className="aside-section">
        <div className="aside-label">워크플로우</div>
        <div className="wf-list">
          <div className="wf-row current">
            <span className="wf-num">01</span>
            <span className="wf-name">작업</span>
            <span className="wf-marker">현재</span>
          </div>
          <div className="wf-row">
            <span className="wf-num">02</span>
            <span className="wf-name">에이전트 전달</span>
            <span className="wf-marker">-</span>
          </div>
          <div className="wf-row">
            <span className="wf-num">03</span>
            <span className="wf-name">검토 및 공유</span>
            <span className="wf-marker">-</span>
          </div>
        </div>
      </section>
    </div>
  );
}
