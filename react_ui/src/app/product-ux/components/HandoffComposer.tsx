import * as RadioGroup from "@radix-ui/react-radio-group";

import { HandoffMode, TaskActionId, TaskRecord } from "../types";

interface HandoffComposerProps {
  onChangeHandoffMode: (mode: HandoffMode) => void;
  onOpenContext: () => void;
  onTriggerAction: (actionId: TaskActionId) => void;
  task: TaskRecord;
}

function taskReference(task: TaskRecord): string {
  return task.sources.find((source) => source.type === "Jira")?.title ?? task.id.toUpperCase();
}

export function HandoffComposer({ onChangeHandoffMode, onOpenContext, onTriggerAction, task }: HandoffComposerProps) {
  const primaryAction = task.actions.find((action) => action.kind === "primary");
  const activeAgent = task.connectedAgents.find((agent) => agent.roleId === task.activeBrief.roleId) ?? task.connectedAgents[0];

  return (
    <section className="handoff-screen">
      <header className="title-block">
        <div className="eyebrow-row">
          <span className="task-id">{taskReference(task)}</span>
          <span className="status-pill">
            <span className="status-dot" />
            {task.stageLabel}
          </span>
          <span className="sprint-tag">{task.activeBrief.roleLabel}</span>
        </div>

        <h2 className="task-h1">{task.activeBrief.title}</h2>
        <p className="task-desc">{task.activeBrief.instruction}</p>
      </header>

      <section className="col-main">
        <div className="section-header">보낼 브리프</div>

        <article className="handoff-doc-sheet">
          <pre className="handoff-brief-body">{task.activeBrief.body}</pre>
        </article>

        <section className="handoff-subsection">
          <div className="section-header">완료 기준</div>
          <div className="props props--compact">
            <article className="prop">
              <div className="prop-label">기대 결과</div>
              <div className="prop-value">{task.activeBrief.expectedResponse}</div>
            </article>

            <div className="prop-divider" />

            <article className="prop">
              <div className="prop-label">보내기 전 체크</div>
              <ul className="review-checklist review-checklist--compact">
                {task.activeBrief.checklist.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </article>

            <div className="prop-divider" />

            <article className="prop">
              <div className="prop-label">포함된 맥락</div>
              <div className="prop-value muted">{task.activeBrief.contextIncluded.join(", ")}</div>
            </article>

            <div className="prop-divider" />

            <article className="prop">
              <div className="prop-label">파일 handoff 경로</div>
              <div className="path-contract">
                <div className="path-contract__item">
                  <span className="path-contract__label">읽을 파일</span>
                  <code>{task.activeBrief.handoffPath}</code>
                </div>
                <div className="path-contract__item">
                  <span className="path-contract__label">결과 파일</span>
                  <code>{task.activeBrief.responsePath}</code>
                </div>
              </div>
            </article>
          </div>
        </section>

        <div className="task-document__actions">
          {primaryAction ? (
            <button className="button button--primary button--wide" onClick={() => onTriggerAction(primaryAction.id)} type="button">
              {primaryAction.label}
            </button>
          ) : null}
          <button className="button button--secondary" onClick={onOpenContext} type="button">
            맥락 열기
          </button>
        </div>
      </section>

      <aside className="col-aside">
        <div className="aside-stack">
          <section className="aside-section">
            <div className="aside-label">전달 방식</div>
            <RadioGroup.Root className="mode-selector" onValueChange={(value) => onChangeHandoffMode(value as HandoffMode)} value={task.handoffMode}>
              {task.handoffModeOptions.map((mode) => (
                <label key={mode.id} className="mode-option">
                  <RadioGroup.Item className="mode-option__control" value={mode.id}>
                    <RadioGroup.Indicator className="mode-option__indicator" />
                  </RadioGroup.Item>
                  <div className="mode-option__copy">
                    <strong>{mode.label}</strong>
                    <span>{mode.helper}</span>
                  </div>
                </label>
              ))}
            </RadioGroup.Root>
          </section>

          <section className="aside-section">
            <div className="aside-label">전달 대상</div>
            <div className="status-block-list">
              <article className="status-block">
                <span className="eyebrow">현재 에이전트</span>
                <strong>{activeAgent ? `${activeAgent.name} / ${activeAgent.productLabel}` : task.activeBrief.roleLabel}</strong>
                <p>{activeAgent?.statusNote ?? "Use your connected agent for this role."}</p>
              </article>

              <article className="status-block">
                <span className="eyebrow">다음 단계에서 확인할 결과</span>
                <strong>{task.activeBrief.expectedResponse}</strong>
                <p>내 에이전트가 결과 파일을 남기면, 이 작업 공간에서는 완료 여부만 확인하고 다음 단계로 넘어갑니다.</p>
              </article>

              <article className="status-block status-block--muted">
                <span className="eyebrow">수동 handoff</span>
                <strong>{task.handoffMode === "file_handoff" ? "이 요청 파일을 읽고 결과 파일을 남기게 합니다." : "내 에이전트 채팅에서 작업을 이어갑니다."}</strong>
                <p>
                  {task.handoffMode === "file_handoff"
                    ? `${task.activeBrief.handoffPath}를 전달하고 ${task.activeBrief.responsePath}에 결과가 남으면, 이 작업 공간으로 돌아와 다음 단계를 확인합니다.`
                    : "브리프를 자신의 에이전트 채팅에 붙여넣고, 작업이 끝나면 이 작업 공간으로 돌아와 다음 단계를 확인합니다."}
                </p>
              </article>
            </div>
          </section>
        </div>
      </aside>
    </section>
  );
}
