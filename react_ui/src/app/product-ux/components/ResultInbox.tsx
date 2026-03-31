import { AgentRecord, ResultItem, TaskRecord } from "../types";

interface ResultInboxProps {
  agents: AgentRecord[];
  task: TaskRecord;
}

function agentName(agents: AgentRecord[], agentId: string) {
  return agents.find((agent) => agent.id === agentId)?.name ?? agentId;
}

export function ResultInbox({ agents, task }: ResultInboxProps) {
  return (
    <section className="agent-panel">
      <div className="agent-panel__header">
        <div>
          <span className="agent-kicker">Result Inbox</span>
          <h3>에이전트가 돌려준 결과</h3>
        </div>
        <span className="agent-counter">{task.results.length} items</span>
      </div>
      <div className="result-list">
        {task.results.map((result: ResultItem) => (
          <article key={result.id} className="result-item">
            <div className="result-item__topline">
              <strong>{result.title}</strong>
              <span className={`result-badge result-badge--${result.status}`}>{result.status}</span>
            </div>
            <p>{result.summary}</p>
            <div className="result-item__meta">
              <span>{agentName(agents, result.fromAgentId)}</span>
              <span>{result.updatedAt}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

