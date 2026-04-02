import {
  AgentRecord,
  AgentRoleId,
  ConnectedAgentRecord,
  HandoffMode,
  HandoffModeOption,
  ProductExperience,
  ProductViewId,
  ResultItem,
  ShareStatus,
  TaskAction,
  TaskActionId,
  TaskBriefTemplate,
  TaskDisplayState,
  TaskRecord,
} from "./types";

interface TaskScenario {
  id: string;
  isPrimaryDemo: boolean;
  title: string;
  account: string;
  summary: string;
  objective: string;
  dueLabel: string;
  urgency: string;
  initialState: TaskDisplayState;
  initialRole: AgentRoleId;
  initialHandoffMode: HandoffMode;
  reviewOutcomeState: "ready_for_decision" | "revise";
  connectedAgentIds: string[];
  pmBrief: TaskBriefTemplate;
  criticBrief: TaskBriefTemplate;
  pmResult: ResultItem;
  criticResult?: ResultItem;
  contextEntries: TaskRecord["contextEntries"];
  sources: TaskRecord["sources"];
  shareStates: {
    working: ShareStatus[];
    ready: ShareStatus[];
    shared: ShareStatus[];
  };
  reviewCopy: {
    reviseHeadline: string;
    reviseSummary: string;
    readyHeadline: string;
    readySummary: string;
    sharedHeadline: string;
    sharedSummary: string;
  };
}

interface TaskRuntime {
  displayState: TaskDisplayState;
  activeRole: AgentRoleId;
  handoffMode: HandoffMode;
  updatedAt: string;
}

const DEMO_DRAFT_REQUEST_PATH = "project/runs/demo_requirements_draft_request.md";
const DEMO_DRAFT_OUTPUT_PATH = "project/artifacts/demo_requirements_draft.md";
const DEMO_REVIEW_REQUEST_PATH = "project/runs/demo_requirements_review_request.md";
const DEMO_REVIEW_OUTPUT_PATH = "project/artifacts/demo_requirements_review.md";

const HANDOFF_MODES: HandoffModeOption[] = [
  {
    id: "file_handoff",
    label: "파일 handoff",
    helper: "요청 파일 경로를 전달하고, 결과 파일이 준비되면 이 화면으로 돌아와 다음 단계를 확인합니다.",
  },
  {
    id: "copy_paste",
    label: "복사 후 붙여넣기",
    helper: "보조 옵션입니다. 브리프를 에이전트 채팅에 붙여넣고, 작업이 끝나면 이 화면으로 돌아와 다음 단계를 확인합니다.",
  },
];

const AGENTS: AgentRecord[] = [
  {
    id: "pm-agent",
    name: "내 에이전트",
    roleId: "pm",
    roleLabel: "PM Agent",
    responsibility: "Drafts the first brief the team can react to.",
    productLabel: "Personal agent",
    focus: "brief drafting",
    status: "connected",
    statusNote: "다음 PM handoff를 바로 이어갈 수 있는 상태입니다.",
  },
  {
    id: "critic-agent",
    name: "내 에이전트",
    roleId: "critic",
    roleLabel: "Critic Agent",
    responsibility: "Checks clarity, missing decisions, and share readiness.",
    productLabel: "Personal agent",
    focus: "quality review",
    status: "connected",
    statusNote: "PM 초안이 돌아오면 바로 검토를 시작할 수 있습니다.",
  },
  {
    id: "ops-agent",
    name: "작업 공간",
    roleId: "ops",
    roleLabel: "Ops Agent",
    responsibility: "Prepares the final Jira and Confluence share state.",
    productLabel: "Workspace",
    focus: "team share",
    status: "waiting",
    statusNote: "운영자가 마지막 공유 단계를 확인하기를 기다리고 있습니다.",
  },
];

const agentMap = new Map(AGENTS.map((agent) => [agent.id, agent]));

const SCENARIOS: TaskScenario[] = [
  {
    id: "task-japan-launch",
    isPrimaryDemo: true,
    title: "점포 운영 AI 적용 범위 정리",
    account: "점포 운영 DX 파일럿",
    summary: "점포 운영 문의 대응 업무를 기준으로, 1차 적용 범위와 요구사항 정의서 초안을 정리합니다.",
    objective: "반복 문의 패턴을 기준으로 도입 범위, 빠진 담당자, 팀 공유 전에 남은 결정 사항을 정리합니다.",
    dueLabel: "오늘 18:00 KST",
    urgency: "오늘 검토 전에 초안이 필요합니다",
    initialState: "brief_ready",
    initialRole: "pm",
    initialHandoffMode: "file_handoff",
    reviewOutcomeState: "ready_for_decision",
    connectedAgentIds: ["pm-agent", "critic-agent", "ops-agent"],
    pmBrief: {
      roleId: "pm",
      roleLabel: "PM Agent",
      title: "요구사항 정의서 초안 준비",
      instruction: "점포 운영 문의 대응 업무를 기준으로 첫 적용 범위와 요구사항 정의서 초안을 정리합니다.",
      body: `# 요구사항 정의서 초안 준비

목표
- 점포 운영 문의 대응 업무를 기준으로 첫 적용 범위를 정리합니다.
- 비개발자 팀이 직접 운영할 수 있는 수준으로 요구사항을 묶습니다.
- 팀 공유 전에 남은 결정 사항과 빠진 담당자를 끝에 정리합니다.

출력
- 요구사항 정의서 초안 1개
- 열린 질문 목록 1개`,
      checklist: [
        "적용 범위와 운영 목표를 한 번에 읽히게 적습니다.",
        "빠진 담당자와 결정이 필요한 항목을 구분합니다.",
        "팀 공유 전에 확인할 마지막 판단 포인트를 끝에 남깁니다.",
      ],
      expectedResponse: "요구사항 정의서 초안 1개와 열린 질문 목록 1개",
      contextIncluded: ["03_Context", "점포 운영 인터뷰 메모", "현재 Jira 작업 상태"],
      handoffPath: DEMO_DRAFT_REQUEST_PATH,
      responsePath: DEMO_DRAFT_OUTPUT_PATH,
    },
    criticBrief: {
      roleId: "critic",
      roleLabel: "Critic Agent",
      title: "요구사항 초안 검토 요청",
      instruction: "초안이 팀 공유 가능한 수준인지, 빠진 담당자와 결정이 없는지 검토합니다.",
      body: `# 요구사항 초안 검토 요청

PM 초안을 읽고 아래를 확인합니다.
- 점포 운영 팀과 공유하기 전에 아직 빠진 내용이 있는가?
- 비개발자 운영팀이 읽어도 충분히 명확한가?
- 지금 공유해도 되는가, 아니면 한 번 더 수정해야 하는가?

출력
- verdict: ready_for_decision 또는 revise
- 요약
- 권장 수정 사항`,
      checklist: [
        "빠진 담당자나 미확정 결정을 짚어줍니다.",
        "지금 팀 공유가 가능한지 판단합니다.",
        "운영자의 다음 행동을 추천합니다.",
      ],
      expectedResponse: "짧은 검토 verdict와 권장 수정 사항",
      contextIncluded: ["요구사항 정의서 초안", "03_Context", "팀 공유 기준"],
      handoffPath: DEMO_REVIEW_REQUEST_PATH,
      responsePath: DEMO_REVIEW_OUTPUT_PATH,
    },
    pmResult: {
      id: "result-japan-launch-draft",
      title: "요구사항 정의서 초안",
      fromAgentLabel: "내 에이전트",
      summary: "1차 적용 범위, 빠진 담당자, 팀 공유 전에 확인할 결정 사항을 정리했습니다.",
      status: "ready",
      updatedAt: "방금 전",
    },
    criticResult: {
      id: "result-japan-launch-review",
      title: "요구사항 초안 검토 의견",
      fromAgentLabel: "내 에이전트",
      summary: "팀 공유 전에 담당자 공백 1건과 운영 의존성 1건을 더 확인해야 합니다.",
      status: "review",
      updatedAt: "방금 전",
    },
    contextEntries: [
      { id: "japan-goal", label: "목표", value: "반복 문의 대응 업무를 기준으로 첫 적용 범위와 운영 원칙을 한 장으로 정리한다." },
      { id: "japan-gap", label: "열린 이슈", value: "법무 검토 범위와 매장 운영팀 승인 순서가 아직 완전히 확정되지 않았다." },
      { id: "japan-share", label: "공유 기준", value: "Jira와 Confluence에 같은 요약과 같은 다음 행동이 보이도록 정리한다." },
    ],
    sources: [
      { id: "japan-source-context", title: "03_Context", type: "Confluence", freshness: "오늘 업데이트", note: "점포 운영 제약 사항과 범위 기준" },
      { id: "japan-source-task", title: "KAN-12", type: "Jira", freshness: "방금 전 업데이트", note: "현재 데모 작업의 상태와 다음 공유 단계" },
      { id: "japan-source-note", title: "점포 운영 인터뷰 메모", type: "Workspace note", freshness: "오늘 오전 수정", note: "반복 문의 패턴과 빠진 담당자" },
    ],
    shareStates: {
      working: [
        { system: "Jira", label: "팀 공유용 정리 중", detail: "작업은 진행 중이지만 팀이 볼 최종 요구사항 요약은 아직 게시되지 않았습니다.", tone: "healthy", updatedAt: "2분 전" },
        { system: "Confluence", label: "초안 공유 전", detail: "검토된 요구사항 초안이 올라오기 전이라 공유 페이지가 아직 대기 중입니다.", tone: "pending", updatedAt: "아직 게시 전" },
      ],
      ready: [
        { system: "Jira", label: "팀 공유 확인 대기", detail: "최신 초안과 검토 결과가 작업에 연결되어 있고 운영자 확인만 남았습니다.", tone: "healthy", updatedAt: "방금 전" },
        { system: "Confluence", label: "공유 여부 판단 대기", detail: "정의서 페이지는 준비되었지만 운영자가 공유 여부를 아직 결정하지 않았습니다.", tone: "attention", updatedAt: "판단 대기" },
      ],
      shared: [
        { system: "Jira", label: "팀과 공유됨", detail: "최신 요구사항 요약과 다음 행동이 Jira 작업에서 바로 보입니다.", tone: "healthy", updatedAt: "방금 전" },
        { system: "Confluence", label: "팀과 공유됨", detail: "점포 운영팀이 한곳에서 읽을 수 있도록 요구사항 초안이 게시되었습니다.", tone: "healthy", updatedAt: "방금 전" },
      ],
    },
    reviewCopy: {
      reviseHeadline: "한 번 더 수정이 필요합니다.",
      reviseSummary: "검토 결과 빠진 담당자와 운영 의존성이 남아 있어 팀 공유 전에 초안을 한 번 더 다듬어야 합니다.",
      readyHeadline: "최종 팀 공유 판단만 남았습니다.",
      readySummary: "검토는 끝났고, 이제 운영자가 마지막 공유 여부를 확인하면 됩니다.",
      sharedHeadline: "최신 버전이 이미 공유되었습니다.",
      sharedSummary: "Jira와 Confluence에 같은 요구사항 요약과 같은 다음 행동이 반영되어 있습니다.",
    },
  },
  {
    id: "task-pricing-impact",
    isPrimaryDemo: false,
    title: "가격 변경 요약",
    account: "Billing update",
    summary: "PM 브리프는 이미 전달되었고, 검토 요청 전에 응답을 기다리는 상태입니다.",
    objective: "가격 변경이 FAQ 문구와 고객 안내 문안에 어떤 영향을 주는지 짧은 노트로 정리합니다.",
    dueLabel: "내일 11:00 JST",
    urgency: "지원 문구를 당일 안에 정리해야 합니다",
    initialState: "waiting_for_agent",
    initialRole: "pm",
    initialHandoffMode: "file_handoff",
    reviewOutcomeState: "ready_for_decision",
    connectedAgentIds: ["pm-agent", "critic-agent", "ops-agent"],
    pmBrief: {
      roleId: "pm",
      roleLabel: "PM Agent",
      title: "Pricing impact PM brief",
      instruction: "Summarize the customer-facing impact of the pricing change in one short team note.",
      body: `# Pricing impact PM brief

Goal
- Explain what changed in the pricing package.
- Highlight what support and PM need to update.
- Call out any owner or FAQ wording that still needs a decision.

Output
- One short impact note
- One list of open follow-ups`,
      checklist: [
        "Separate customer-facing wording from internal owner follow-up.",
        "Note the FAQ change clearly.",
        "End with the one thing support still needs.",
      ],
      expectedResponse: "One short impact note and one follow-up list",
      contextIncluded: ["pricing proposal", "FAQ draft", "customer messaging guidance"],
      handoffPath: "project/runs/pricing-impact-brief.md",
      responsePath: "pricing-impact-response.md",
    },
    criticBrief: {
      roleId: "critic",
      roleLabel: "Critic Agent",
      title: "Pricing impact review brief",
      instruction: "Check whether the impact note is clear enough for team share and whether any owner is still missing.",
      body: `# Pricing impact Critic brief

Review the impact note and answer:
- Is the note clear enough to share with support and PM?
- Are any owners or FAQ actions still missing?
- Should we share now, or revise first?`,
      checklist: [
        "Check clarity for support and PM readers.",
        "Call out missing owners or FAQ gaps.",
        "Recommend share now or revise.",
      ],
      expectedResponse: "A share verdict and one short review summary",
      contextIncluded: ["PM note", "FAQ draft", "pricing proposal"],
      handoffPath: "project/runs/pricing-impact-review.md",
      responsePath: "pricing-impact-review.md",
    },
    pmResult: {
      id: "result-pricing-impact-draft",
      title: "Pricing impact note",
      fromAgentLabel: "My Codex",
      summary: "Summarized wording changes, FAQ impact, and the owner follow-up still needed before broadcast.",
      status: "ready",
      updatedAt: "7 min ago",
    },
    criticResult: {
      id: "result-pricing-impact-review",
      title: "Pricing impact review",
      fromAgentLabel: "My Claude",
      summary: "The note is readable for the team. One FAQ owner check is still worth confirming, but it is ready for operator decision.",
      status: "review",
      updatedAt: "3 min ago",
    },
    contextEntries: [
      { id: "pricing-goal", label: "Goal", value: "Give PM and support one aligned summary they can use without re-reading the entire proposal." },
      { id: "pricing-gap", label: "Open gap", value: "The FAQ owner is still not final, but the wording direction is stable." },
      { id: "pricing-share", label: "Share expectation", value: "The team should see the same summary in both Jira and Confluence." },
    ],
    sources: [
      { id: "pricing-source-proposal", title: "Pricing proposal", type: "Workspace note", freshness: "Updated this morning", note: "Change summary and rationale" },
      { id: "pricing-source-task", title: "BILL-88", type: "Jira", freshness: "Updated 20 min ago", note: "Owner confirmation and due date" },
      { id: "pricing-source-faq", title: "Support FAQ draft", type: "Confluence", freshness: "Draft only", note: "Still waiting for final publish" },
    ],
    shareStates: {
      working: [
        { system: "Jira", label: "에이전트 응답 대기", detail: "브리프는 이미 전달되었습니다. 응답이 돌아오면 Jira가 함께 갱신됩니다.", tone: "pending", updatedAt: "16분 전" },
        { system: "Confluence", label: "팀 공유 페이지 없음", detail: "아직 진행 중인 작업이라 공유 페이지가 준비되지 않았습니다.", tone: "pending", updatedAt: "아직 게시 전" },
      ],
      ready: [
        { system: "Jira", label: "공유 판단 준비 완료", detail: "영향 요약과 검토 결과가 작업 맥락에 연결되어 운영자 확인만 남았습니다.", tone: "healthy", updatedAt: "3분 전" },
        { system: "Confluence", label: "공유 페이지 준비 완료", detail: "운영자가 공유 단계를 확인하면 바로 게시할 수 있습니다.", tone: "attention", updatedAt: "판단 대기" },
      ],
      shared: [
        { system: "Jira", label: "팀과 공유됨", detail: "최종 영향 요약과 다음 행동이 작업에 반영되어 있습니다.", tone: "healthy", updatedAt: "방금 전" },
        { system: "Confluence", label: "팀과 공유됨", detail: "지원팀이 읽을 수 있도록 공유 작업 공간에 게시되었습니다.", tone: "healthy", updatedAt: "방금 전" },
      ],
    },
    reviewCopy: {
      reviseHeadline: "초안에 한 번 더 수정이 필요합니다.",
      reviseSummary: "검토 결과 문구나 담당자 공백이 남아 있어 지금 공유하기에는 이릅니다.",
      readyHeadline: "최종 공유 판단만 남았습니다.",
      readySummary: "검토는 끝났고, 이제 운영자 확인만 남았습니다.",
      sharedHeadline: "이 요약은 이미 공유되었습니다.",
      sharedSummary: "최신 가격 변경 요약이 Jira와 Confluence에 반영되어 있습니다.",
    },
  },
  {
    id: "task-retro-share",
    isPrimaryDemo: false,
    title: "점포 운영 회고 공유",
    account: "Post-launch ops",
    summary: "검토는 끝났고, 이제 운영자가 최종 공유 여부와 팀 공지 문구를 결정하는 단계입니다.",
    objective: "다음 주 바로 행동으로 이어질 수 있는 회고 요약을 팀과 공유합니다.",
    dueLabel: "금요일 17:00 KST",
    urgency: "이번 주 안에 공유가 필요합니다",
    initialState: "ready_for_decision",
    initialRole: "ops",
    initialHandoffMode: "copy_paste",
    reviewOutcomeState: "ready_for_decision",
    connectedAgentIds: ["pm-agent", "critic-agent", "ops-agent"],
    pmBrief: {
      roleId: "pm",
      roleLabel: "PM Agent",
      title: "Retro summary PM brief",
      instruction: "Turn the retro notes into one short summary the team can act on next week.",
      body: `# Retro summary PM brief

Goal
- Keep only action-oriented takeaways.
- Attach owners where needed.
- End with the next move for next week.`,
      checklist: [
        "Keep the note short and action-led.",
        "Attach owners where needed.",
        "End with next week's follow-up.",
      ],
      expectedResponse: "A one-page retro summary",
      contextIncluded: ["retro notes", "follow-up task list", "share criteria"],
      handoffPath: "project/runs/retro-summary.md",
      responsePath: "retro-summary-response.md",
    },
    criticBrief: {
      roleId: "critic",
      roleLabel: "Critic Agent",
      title: "Retro review brief",
      instruction: "Check if the retro summary is clear enough to share and whether any action owner is still missing.",
      body: `# Retro Critic brief

Review the retro summary and answer:
- Is the next action clear enough for the launch squad?
- Are any owners missing?
- Should we share now or revise first?`,
      checklist: [
        "Check missing owners.",
        "Check clarity of next action.",
        "Recommend share now or revise.",
      ],
      expectedResponse: "A share verdict and one review summary",
      contextIncluded: ["retro summary", "follow-up actions", "team share criteria"],
      handoffPath: "project/runs/retro-review.md",
      responsePath: "retro-review-response.md",
    },
    pmResult: {
      id: "result-retro-summary",
      title: "Retro summary",
      fromAgentLabel: "My Codex",
      summary: "Condensed the retro into owner-linked actions and one follow-up focus for next week.",
      status: "ready",
      updatedAt: "34 min ago",
    },
    criticResult: {
      id: "result-retro-review",
      title: "Retro review",
      fromAgentLabel: "My Claude",
      summary: "The summary is ready for the operator's final decision before team share.",
      status: "review",
      updatedAt: "27 min ago",
    },
    contextEntries: [
      { id: "retro-goal", label: "Goal", value: "Share one retro note the launch squad can turn into follow-up work immediately." },
      { id: "retro-gap", label: "Open gap", value: "The last pass is about phrasing and share timing, not content discovery." },
      { id: "retro-share", label: "Share expectation", value: "Jira and Confluence should show the same summary and follow-up focus." },
    ],
    sources: [
      { id: "retro-source-notes", title: "Retro raw notes", type: "Workspace note", freshness: "Written this week", note: "Original meeting notes and follow-up items" },
      { id: "retro-source-page", title: "Retro publish page", type: "Confluence", freshness: "Draft saved", note: "Waiting for final share confirmation" },
      { id: "retro-source-followups", title: "Launch follow-up list", type: "Jira", freshness: "Reference", note: "Related execution tasks" },
    ],
    shareStates: {
      working: [
        { system: "Jira", label: "참고 링크만 연결됨", detail: "후속 작업 티켓은 연결되어 있지만 요약은 아직 공유되지 않았습니다.", tone: "pending", updatedAt: "참고용" },
        { system: "Confluence", label: "초안 페이지만 존재", detail: "회고 페이지는 만들어졌지만 아직 초안 상태입니다.", tone: "attention", updatedAt: "초안 상태" },
      ],
      ready: [
        { system: "Jira", label: "팀 공유 준비 완료", detail: "후속 작업 목록과 회고 요약을 함께 보여줄 준비가 되었습니다.", tone: "healthy", updatedAt: "5분 전" },
        { system: "Confluence", label: "최종 확인 대기", detail: "운영자가 공유 단계를 확인하면 회고 페이지를 바로 게시할 수 있습니다.", tone: "attention", updatedAt: "판단 대기" },
      ],
      shared: [
        { system: "Jira", label: "팀과 공유됨", detail: "회고 요약이 Jira에서 같은 다음 행동을 가리키고 있습니다.", tone: "healthy", updatedAt: "방금 전" },
        { system: "Confluence", label: "팀과 공유됨", detail: "게시된 회고 노트를 런치 팀 전체가 볼 수 있습니다.", tone: "healthy", updatedAt: "방금 전" },
      ],
    },
    reviewCopy: {
      reviseHeadline: "마지막 수정이 한 번 더 필요합니다.",
      reviseSummary: "문구상 큰 이슈가 하나 남아 있어 팀 공유 전에 한 번 더 다듬어야 합니다.",
      readyHeadline: "최종 공유 판단만 남았습니다.",
      readySummary: "검토는 완료되었고, 이제 운영자의 공유 결정만 남았습니다.",
      sharedHeadline: "이 요약은 이미 공유되었습니다.",
      sharedSummary: "Jira와 Confluence에 같은 회고 요약과 후속 방향이 보입니다.",
    },
  },
];

const INITIAL_RUNTIME: Record<string, TaskRuntime> = Object.fromEntries(
  SCENARIOS.map((scenario) => [
    scenario.id,
    {
      displayState: scenario.initialState,
      activeRole: scenario.initialRole,
      handoffMode: scenario.initialHandoffMode,
      updatedAt: "Just now",
    },
  ]),
);

function scenarioById(taskId: string): TaskScenario {
  const scenario = SCENARIOS.find((item) => item.id === taskId);
  if (!scenario) {
    throw new Error(`Unknown task scenario: ${taskId}`);
  }

  return scenario;
}

function statusLabel(state: TaskDisplayState): string {
  switch (state) {
    case "not_started":
      return "시작 전";
    case "brief_ready":
      return "브리프 준비";
    case "waiting_for_agent":
      return "작업 진행 중";
    case "response_received":
      return "작업 완료 확인";
    case "review_requested":
      return "검토 요청 준비";
    case "ready_for_decision":
      return "판단 필요";
    case "revise":
      return "수정 필요";
    case "shared":
      return "공유 완료";
    default:
      return "진행 중";
  }
}

function nextAction(state: TaskDisplayState): { label: string; detail: string } {
  switch (state) {
    case "not_started":
      return {
        label: "브리프 준비",
        detail: "에이전트에게 넘기기 전에 먼저 브리프를 정리합니다.",
      };
    case "brief_ready":
      return {
        label: "에이전트에 보내기",
        detail: "요청 파일이 준비되었습니다. 내 에이전트에 전달해 초안 작성을 시작합니다.",
      };
    case "waiting_for_agent":
      return {
        label: "작업 완료 확인",
        detail: "handoff가 나간 상태입니다. 내 에이전트가 결과 파일을 남겼는지 확인하고 다음 단계로 넘깁니다.",
      };
    case "response_received":
      return {
        label: "검토 요청",
        detail: "초안이 돌아왔습니다. Critic 역할로 다음 handoff를 준비합니다.",
      };
    case "review_requested":
      return {
        label: "에이전트에 보내기",
        detail: "검토 요청 파일이 준비되었습니다. Critic 에이전트에 보내고 검토 결과를 기다립니다.",
      };
    case "ready_for_decision":
      return {
        label: "팀 공유 준비",
        detail: "검토가 끝났습니다. Jira와 Confluence에 반영할 최종 공유 상태를 확인합니다.",
      };
    case "revise":
      return {
        label: "수정 반영",
        detail: "검토 피드백을 반영해 초안을 다듬고 한 번 더 보냅니다.",
      };
    case "shared":
      return {
        label: "공유 상태 확인",
        detail: "작업이 공유된 상태입니다. 팀이 같은 최종 요약을 보는지 확인합니다.",
      };
    default:
      return {
        label: "계속 진행",
        detail: "다음 단계로 작업을 이어갑니다.",
      };
  }
}

function actionsForState(state: TaskDisplayState): TaskAction[] {
  switch (state) {
    case "not_started":
      return [{ id: "prepare_brief", label: "브리프 준비", helper: "다음 handoff를 위해 브리프를 정리합니다.", kind: "primary", enabled: true }];
    case "brief_ready":
      return [{ id: "mark_sent", label: "에이전트에 보내기", helper: "요청 파일을 전달하고 작업 대기 상태로 넘깁니다.", kind: "primary", enabled: true }];
    case "waiting_for_agent":
      return [{ id: "receive_result", label: "작업 완료 확인", helper: "내 에이전트가 결과 파일을 남겼는지 확인하고 다음 단계로 진행합니다.", kind: "primary", enabled: true }];
    case "response_received":
      return [{ id: "request_review", label: "검토 요청", helper: "PM 초안을 기준으로 Critic handoff를 준비합니다.", kind: "primary", enabled: true }];
    case "review_requested":
      return [{ id: "mark_sent", label: "에이전트에 보내기", helper: "검토 요청 파일을 전달하고 검토 결과를 기다립니다.", kind: "primary", enabled: true }];
    case "ready_for_decision":
      return [{ id: "confirm_share", label: "팀 공유 준비", helper: "Jira와 Confluence에 보여줄 최종 공유 상태를 확인합니다.", kind: "primary", enabled: true }];
    case "revise":
      return [{ id: "apply_review", label: "수정 반영", helper: "검토 피드백을 반영해 한 번 더 다듬습니다.", kind: "primary", enabled: true }];
    case "shared":
      return [{ id: "confirm_share", label: "공유 상태 확인", helper: "최종 공유 상태를 다시 확인합니다.", kind: "primary", enabled: true }];
    default:
      return [];
  }
}

function shareStatusesForState(scenario: TaskScenario, state: TaskDisplayState): ShareStatus[] {
  if (state === "shared") {
    return scenario.shareStates.shared;
  }

  if (state === "ready_for_decision" || state === "revise") {
    return scenario.shareStates.ready;
  }

  return scenario.shareStates.working;
}

function resultsForState(scenario: TaskScenario, runtime: TaskRuntime): ResultItem[] {
  const results: ResultItem[] = [];
  const hasPmResult =
    runtime.displayState === "response_received" ||
    runtime.displayState === "review_requested" ||
    runtime.displayState === "ready_for_decision" ||
    runtime.displayState === "revise" ||
    runtime.displayState === "shared" ||
    (runtime.displayState === "waiting_for_agent" && runtime.activeRole === "critic");

  const hasCriticResult =
    runtime.displayState === "ready_for_decision" || runtime.displayState === "revise" || runtime.displayState === "shared";

  if (hasPmResult) {
    results.push(scenario.pmResult);
  }

  if (hasCriticResult && scenario.criticResult) {
    results.push(scenario.criticResult);
  }

  return results;
}

function reviewCopyForState(scenario: TaskScenario, state: TaskDisplayState) {
  if (state === "revise") {
    return {
      headline: scenario.reviewCopy.reviseHeadline,
      summary: scenario.reviewCopy.reviseSummary,
      outcomeState: "revise" as const,
      operatorDecisionLabel: "팀 공유 전 수정 필요",
      operatorDecisionDetail: "팀에 게시하기 전에 검토 피드백을 반영해 초안을 한 번 더 다듬습니다.",
      reviewChecklist: ["빠진 담당자를 명확히 합니다.", "일정 의존성을 정리합니다.", "공유 전에 한 번 더 검토를 돌립니다."],
    };
  }

  if (state === "shared") {
    return {
      headline: scenario.reviewCopy.sharedHeadline,
      summary: scenario.reviewCopy.sharedSummary,
      outcomeState: "ready_for_decision" as const,
      operatorDecisionLabel: "공유 상태 확인 완료",
      operatorDecisionDetail: "운영자가 최종 공유 상태를 이미 확인했고, 이제 팀은 Jira와 Confluence에서 같은 결과를 볼 수 있습니다.",
      reviewChecklist: ["두 시스템의 요약이 같은지 확인합니다.", "다음 행동이 잘 보이는지 확인합니다.", "공유 시점 확인이 완료되었습니다."],
    };
  }

  return {
    headline: scenario.reviewCopy.readyHeadline,
    summary: scenario.reviewCopy.readySummary,
    outcomeState: "ready_for_decision" as const,
    operatorDecisionLabel: "운영자 최종 판단 필요",
    operatorDecisionDetail: "Critic 검토는 끝났습니다. 이제 요약과 공유 대상을 확인한 뒤 마지막 공유 단계를 확정합니다.",
    reviewChecklist: [
      "이 요약이 팀에게 바로 전달 가능한지 확인합니다.",
      "Jira와 Confluence에 같은 메시지가 반영되는지 확인합니다.",
      "최종 팀 공유 업데이트를 준비합니다.",
    ],
  };
}

function activeBriefForRuntime(scenario: TaskScenario, runtime: TaskRuntime): TaskBriefTemplate {
  return runtime.activeRole === "critic" ? scenario.criticBrief : scenario.pmBrief;
}

function connectedAgentsForRuntime(scenario: TaskScenario, runtime: TaskRuntime): ConnectedAgentRecord[] {
  return scenario.connectedAgentIds
    .map((id) => agentMap.get(id))
    .filter((agent): agent is AgentRecord => Boolean(agent))
    .map((agent) => {
      const isActive = agent.roleId === runtime.activeRole;
      const isWaitingStage = runtime.displayState === "waiting_for_agent";

      let status = agent.status;
      let statusNote = agent.statusNote;

      if (isActive && isWaitingStage && agent.roleId !== "ops") {
        status = "reviewing";
        statusNote = "이 에이전트가 결과 파일을 남기기를 기다리고 있습니다.";
      } else if (isActive && !isWaitingStage && agent.roleId !== "ops") {
        status = "connected";
        statusNote = "현재 단계에서 실제로 사용하는 역할입니다.";
      } else if (agent.roleId === "ops" && (runtime.displayState === "ready_for_decision" || runtime.displayState === "shared")) {
        status = "connected";
        statusNote = "최종 팀 공유 상태를 확인할 준비가 되어 있습니다.";
      }

      return {
        ...agent,
        status,
        statusNote,
      };
    });
}

function createTaskRecord(scenario: TaskScenario, runtime: TaskRuntime): TaskRecord {
  const action = nextAction(runtime.displayState);
  const reviewCopy = reviewCopyForState(scenario, runtime.displayState);

  return {
    id: scenario.id,
    isPrimaryDemo: scenario.isPrimaryDemo,
    title: scenario.title,
    account: scenario.account,
    summary: scenario.summary,
    objective: scenario.objective,
    dueLabel: scenario.dueLabel,
    updatedAt: runtime.updatedAt,
    urgency: scenario.urgency,
    displayState: runtime.displayState,
    stageLabel: statusLabel(runtime.displayState),
    activeRole: runtime.activeRole,
    nextActionLabel: action.label,
    nextActionDetail: action.detail,
    actions: actionsForState(runtime.displayState),
    handoffMode: runtime.handoffMode,
    handoffModeOptions: HANDOFF_MODES,
    connectedAgents: connectedAgentsForRuntime(scenario, runtime),
    activeBrief: activeBriefForRuntime(scenario, runtime),
    shareStatuses: shareStatusesForState(scenario, runtime.displayState),
    results: resultsForState(scenario, runtime),
    contextEntries: scenario.contextEntries,
    sources: scenario.sources,
    reviewHeadline: reviewCopy.headline,
    reviewSummary: reviewCopy.summary,
    reviewChecklist: reviewCopy.reviewChecklist,
    operatorDecisionLabel: reviewCopy.operatorDecisionLabel,
    operatorDecisionDetail: reviewCopy.operatorDecisionDetail,
    reviewOutcomeState: reviewCopy.outcomeState,
  };
}

function rebuildProduct(previous: ProductExperience, runtimeMap: Record<string, TaskRuntime>): ProductExperience {
  return {
    ...previous,
    tasks: SCENARIOS.map((scenario) => createTaskRecord(scenario, runtimeMap[scenario.id])),
  };
}

function advanceState(previous: TaskRuntime, actionId: TaskActionId, scenario: TaskScenario): TaskRuntime {
  switch (actionId) {
    case "prepare_brief":
      return {
        ...previous,
        displayState: "brief_ready",
        activeRole: "pm",
        updatedAt: "Just now",
      };
    case "mark_sent":
      return {
        ...previous,
        displayState: "waiting_for_agent",
        activeRole: previous.displayState === "review_requested" ? "critic" : previous.activeRole,
        updatedAt: "Just now",
      };
    case "receive_result":
      if (previous.activeRole === "critic") {
        return {
          ...previous,
          displayState: scenario.reviewOutcomeState,
          activeRole: "ops",
          updatedAt: "Just now",
        };
      }

      return {
        ...previous,
        displayState: "response_received",
        activeRole: "pm",
        updatedAt: "Just now",
      };
    case "request_review":
      return {
        ...previous,
        displayState: "review_requested",
        activeRole: "critic",
        updatedAt: "Just now",
      };
    case "apply_review":
      return {
        ...previous,
        displayState: "brief_ready",
        activeRole: "pm",
        updatedAt: "Just now",
      };
    case "confirm_share":
      return {
        ...previous,
        displayState: "shared",
        activeRole: "ops",
        updatedAt: "Just now",
      };
    default:
      return previous;
  }
}

export function preferredViewForTask(task: TaskRecord): ProductViewId {
  switch (task.displayState) {
    case "not_started":
    case "brief_ready":
      return "task";
    case "waiting_for_agent":
    case "response_received":
    case "review_requested":
      return "handoff";
    case "ready_for_decision":
    case "revise":
    case "shared":
      return "review";
    default:
      return "task";
  }
}

export function performTaskAction(product: ProductExperience, taskId: string, actionId: TaskActionId) {
  const scenario = scenarioById(taskId);
  const runtimeMap: Record<string, TaskRuntime> = Object.fromEntries(
    product.tasks.map((task) => [
      task.id,
      {
        displayState: task.displayState,
        activeRole: task.activeRole,
        handoffMode: task.handoffMode,
        updatedAt: task.updatedAt,
      },
    ]),
  );

  runtimeMap[taskId] = advanceState(runtimeMap[taskId], actionId, scenario);

  const nextProduct = rebuildProduct(product, runtimeMap);
  const nextTask = nextProduct.tasks.find((task) => task.id === taskId) ?? nextProduct.tasks[0];

  return {
    product: nextProduct,
    nextView: nextTask ? preferredViewForTask(nextTask) : "task",
  };
}

export function setTaskHandoffMode(product: ProductExperience, taskId: string, mode: HandoffMode): ProductExperience {
  const runtimeMap: Record<string, TaskRuntime> = Object.fromEntries(
    product.tasks.map((task) => [
      task.id,
      {
        displayState: task.displayState,
        activeRole: task.activeRole,
        handoffMode: task.handoffMode,
        updatedAt: task.updatedAt,
      },
    ]),
  );

  runtimeMap[taskId] = {
    ...runtimeMap[taskId],
    handoffMode: mode,
    updatedAt: "Just now",
  };

  return rebuildProduct(product, runtimeMap);
}

export const initialProductExperience: ProductExperience = {
  title: "AI_Japan_project",
  subtitle: "구조화된 프로젝트 맥락을 바탕으로 개인 에이전트가 작업을 이어가는 연결형 작업 공간",
  workspaceLabel: "개인 에이전트 작업 공간",
  workspaceTagline: "구조화된 맥락을 바탕으로 에이전트 handoff를 준비하고, 마지막에는 팀 공유 상태를 확인합니다.",
  agents: AGENTS,
  tasks: SCENARIOS.map((scenario) => createTaskRecord(scenario, INITIAL_RUNTIME[scenario.id])),
};
