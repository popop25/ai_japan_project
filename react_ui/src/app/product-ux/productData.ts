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

const HANDOFF_MODES: HandoffModeOption[] = [
  {
    id: "copy_paste",
    label: "Copy and paste",
    helper: "Copy the brief into your agent chat and paste the response back here.",
  },
  {
    id: "file_handoff",
    label: "File handoff",
    helper: "Send the brief as a file path and bring the response back as a file or paste-back.",
  },
];

const AGENTS: AgentRecord[] = [
  {
    id: "pm-agent",
    name: "My Codex",
    roleId: "pm",
    roleLabel: "PM Agent",
    responsibility: "Drafts the first brief the team can react to.",
    productLabel: "Codex",
    focus: "brief drafting",
    status: "connected",
    statusNote: "Connected and ready for the next PM handoff.",
  },
  {
    id: "critic-agent",
    name: "My Claude",
    roleId: "critic",
    roleLabel: "Critic Agent",
    responsibility: "Checks clarity, missing decisions, and share readiness.",
    productLabel: "Claude",
    focus: "quality review",
    status: "connected",
    statusNote: "Connected for review once the PM draft is back.",
  },
  {
    id: "ops-agent",
    name: "Workspace sync",
    roleId: "ops",
    roleLabel: "Ops Agent",
    responsibility: "Prepares the final Jira and Confluence share state.",
    productLabel: "Workspace",
    focus: "team share",
    status: "waiting",
    statusNote: "Waiting for the operator to confirm the share step.",
  },
];

const agentMap = new Map(AGENTS.map((agent) => [agent.id, agent]));

const SCENARIOS: TaskScenario[] = [
  {
    id: "task-japan-launch",
    title: "Japan launch brief",
    account: "AI Japan launch",
    summary: "Prepare one short launch brief the retail team can review before tomorrow's planning check-in.",
    objective: "Confirm the scope, missing owners, and the next decision before we send a first draft to the team.",
    dueLabel: "Today, 18:00 KST",
    urgency: "Needs a draft before today's review",
    initialState: "brief_ready",
    initialRole: "pm",
    initialHandoffMode: "copy_paste",
    reviewOutcomeState: "revise",
    connectedAgentIds: ["pm-agent", "critic-agent", "ops-agent"],
    pmBrief: {
      roleId: "pm",
      roleLabel: "PM Agent",
      title: "Japan launch PM brief",
      instruction: "Prepare a concise launch brief the team can react to in one read.",
      body: `# Japan launch PM brief

Goal
- Summarize the launch scope in one paragraph.
- Call out missing owners or blockers.
- End with the one decision we still need before team share.

Output
- One draft brief
- One short list of open questions`,
      checklist: [
        "State the launch goal and scope clearly.",
        "Separate missing owners from open blockers.",
        "End with the single next decision the team needs.",
      ],
      expectedResponse: "One brief draft and one list of open questions",
      contextIncluded: ["03_Context summary", "launch decision note", "current Jira task state"],
      handoffPath: "project/runs/japan-launch-brief.md",
      responsePath: "launch-brief-response.md",
    },
    criticBrief: {
      roleId: "critic",
      roleLabel: "Critic Agent",
      title: "Japan launch review brief",
      instruction: "Review the PM draft for missing owners, blockers, and whether it is ready for team share.",
      body: `# Japan launch Critic brief

Review the PM draft and answer:
- What is still missing before we share this with the team?
- Is the summary clear enough for operators and PMs?
- Should we share now, or revise once more?

Output
- Verdict: ready_for_decision or revise
- Summary
- Recommended changes`,
      checklist: [
        "Call out missing owners or blocked decisions.",
        "Check whether the brief can be shared now.",
        "Recommend the operator's next move.",
      ],
      expectedResponse: "A short review verdict and recommended changes",
      contextIncluded: ["PM draft", "launch goal", "team share expectation"],
      handoffPath: "project/runs/japan-launch-review.md",
      responsePath: "launch-review-response.md",
    },
    pmResult: {
      id: "result-japan-launch-draft",
      title: "Launch brief draft v1",
      fromAgentLabel: "My Codex",
      summary: "Drafted a one-page brief with launch scope, open owner gaps, and one final share decision.",
      status: "ready",
      updatedAt: "Just now",
    },
    criticResult: {
      id: "result-japan-launch-review",
      title: "Launch brief review",
      fromAgentLabel: "My Claude",
      summary: "One owner gap and one schedule dependency still need to be clarified before team share.",
      status: "review",
      updatedAt: "Just now",
    },
    contextEntries: [
      { id: "japan-goal", label: "Goal", value: "Share one clear brief the launch squad can align on before tomorrow's planning review." },
      { id: "japan-gap", label: "Open gap", value: "Legal owner and store rollout dependency are still not fully confirmed." },
      { id: "japan-share", label: "Share expectation", value: "Jira and Confluence should show the same next action for the launch team." },
    ],
    sources: [
      { id: "japan-source-context", title: "03_Context", type: "Confluence", freshness: "Updated today", note: "Launch constraints and scope guardrails" },
      { id: "japan-source-task", title: "KAN-9", type: "Jira", freshness: "Updated 12 min ago", note: "Current task owner and due date" },
      { id: "japan-source-note", title: "Launch operator notes", type: "Workspace note", freshness: "Revised this morning", note: "Missing owner and team-share criteria" },
    ],
    shareStates: {
      working: [
        { system: "Jira", label: "Share note is still being prepared", detail: "The task is active, but the team-facing update has not been posted yet.", tone: "healthy", updatedAt: "2 min ago" },
        { system: "Confluence", label: "Draft not shared yet", detail: "The share page is still waiting for a reviewed draft.", tone: "pending", updatedAt: "Not posted yet" },
      ],
      ready: [
        { system: "Jira", label: "Ready for team-share confirmation", detail: "The latest draft and review are connected to the task and ready for operator confirmation.", tone: "healthy", updatedAt: "Just now" },
        { system: "Confluence", label: "Share page waiting for decision", detail: "The page is prepared, but the operator still needs to decide whether to share or revise.", tone: "attention", updatedAt: "Decision pending" },
      ],
      shared: [
        { system: "Jira", label: "Shared with the team", detail: "The latest summary and next action are visible from the task.", tone: "healthy", updatedAt: "Just now" },
        { system: "Confluence", label: "Shared with the team", detail: "The brief is now published for the launch squad to read in one place.", tone: "healthy", updatedAt: "Just now" },
      ],
    },
    reviewCopy: {
      reviseHeadline: "One more revision pass is still needed.",
      reviseSummary: "The review found one missing owner and one schedule dependency, so we should tighten the draft before team share.",
      readyHeadline: "The final team-share decision is ready.",
      readySummary: "The review is complete and only the operator's share decision is left.",
      sharedHeadline: "The latest version is already shared.",
      sharedSummary: "Jira and Confluence now show the same summary and the same next action.",
    },
  },
  {
    id: "task-pricing-impact",
    title: "Pricing change note",
    account: "Billing update",
    summary: "The PM brief has already been sent. We are waiting for the response before we ask for review.",
    objective: "Use one short note to explain how the pricing change affects FAQ wording and customer-facing copy.",
    dueLabel: "Tomorrow, 11:00 JST",
    urgency: "Support copy needs a same-day update",
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
        { system: "Jira", label: "Waiting for the agent response", detail: "The brief is out. Jira will be updated once the response comes back.", tone: "pending", updatedAt: "16 min ago" },
        { system: "Confluence", label: "No team page yet", detail: "A share page has not been prepared because the note is still in progress.", tone: "pending", updatedAt: "Not posted yet" },
      ],
      ready: [
        { system: "Jira", label: "Ready for share decision", detail: "The impact note and review are attached to the task context for the operator to confirm.", tone: "healthy", updatedAt: "3 min ago" },
        { system: "Confluence", label: "Draft share page is staged", detail: "The note can be published as soon as the operator confirms the share step.", tone: "attention", updatedAt: "Decision pending" },
      ],
      shared: [
        { system: "Jira", label: "Shared with the team", detail: "The task now shows the final impact summary and the next action.", tone: "healthy", updatedAt: "Just now" },
        { system: "Confluence", label: "Shared with the team", detail: "The support-facing note is published in the shared workspace.", tone: "healthy", updatedAt: "Just now" },
      ],
    },
    reviewCopy: {
      reviseHeadline: "The draft still needs one more pass.",
      reviseSummary: "The review found a wording or owner gap that makes team share too early.",
      readyHeadline: "This note is ready for the final share decision.",
      readySummary: "The review is complete and the remaining work is operator confirmation.",
      sharedHeadline: "The note has already been shared.",
      sharedSummary: "The latest pricing update is visible in both Jira and Confluence.",
    },
  },
  {
    id: "task-retro-share",
    title: "Store ops retro share",
    account: "Post-launch ops",
    summary: "The review is done. This task is now about the operator's final share decision and the team-facing summary.",
    objective: "Share the retro summary in a form the launch squad can act on immediately next week.",
    dueLabel: "Friday, 17:00 KST",
    urgency: "Needs to go out this week",
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
        { system: "Jira", label: "Reference links only", detail: "The follow-up tickets are linked, but the summary has not been shared yet.", tone: "pending", updatedAt: "Reference only" },
        { system: "Confluence", label: "Draft page only", detail: "The retro page exists, but it is still a draft.", tone: "attention", updatedAt: "Draft only" },
      ],
      ready: [
        { system: "Jira", label: "Ready for team share", detail: "The follow-up task list and the retro summary are ready to be shown together.", tone: "healthy", updatedAt: "5 min ago" },
        { system: "Confluence", label: "Waiting for final confirmation", detail: "The retro page is ready to publish as soon as the operator confirms the share step.", tone: "attention", updatedAt: "Decision pending" },
      ],
      shared: [
        { system: "Jira", label: "Shared with the team", detail: "The retro summary now points the squad to the same next action in Jira.", tone: "healthy", updatedAt: "Just now" },
        { system: "Confluence", label: "Shared with the team", detail: "The published retro note is now available to the full launch squad.", tone: "healthy", updatedAt: "Just now" },
      ],
    },
    reviewCopy: {
      reviseHeadline: "This still needs one final revision.",
      reviseSummary: "One wording issue is still large enough that we should revise before team share.",
      readyHeadline: "The final share decision is ready.",
      readySummary: "The review is complete. The only remaining step is the operator's share decision.",
      sharedHeadline: "The summary is already shared.",
      sharedSummary: "Jira and Confluence now show the same retro summary and follow-up direction.",
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
      return "Not started";
    case "brief_ready":
      return "Brief ready";
    case "waiting_for_agent":
      return "Waiting for response";
    case "response_received":
      return "Response received";
    case "review_requested":
      return "Review brief ready";
    case "ready_for_decision":
      return "Decision needed";
    case "revise":
      return "Revise";
    case "shared":
      return "Shared";
    default:
      return "In progress";
  }
}

function nextAction(state: TaskDisplayState): { label: string; detail: string } {
  switch (state) {
    case "not_started":
      return {
        label: "Brief ready",
        detail: "Prepare the brief before you hand the task to your agent.",
      };
    case "brief_ready":
      return {
        label: "Send to agent",
        detail: "The brief is ready. Send it to your agent to start the draft.",
      };
    case "waiting_for_agent":
      return {
        label: "Receive response",
        detail: "The handoff is out. Bring the response back into the workspace.",
      };
    case "response_received":
      return {
        label: "Request review",
        detail: "The draft is back. Prepare the next handoff for the Critic agent.",
      };
    case "review_requested":
      return {
        label: "Send to agent",
        detail: "The Critic brief is ready. Send it and wait for the review.",
      };
    case "ready_for_decision":
      return {
        label: "Prepare team share",
        detail: "Review is complete. Confirm the final share state for Jira and Confluence.",
      };
    case "revise":
      return {
        label: "Apply review",
        detail: "Tighten the draft with the review feedback, then send it once more.",
      };
    case "shared":
      return {
        label: "Check share status",
        detail: "The task has been shared. Confirm that the team sees the same final summary.",
      };
    default:
      return {
        label: "Continue",
        detail: "Move the task to the next stage.",
      };
  }
}

function actionsForState(state: TaskDisplayState): TaskAction[] {
  switch (state) {
    case "not_started":
      return [{ id: "prepare_brief", label: "Brief ready", helper: "Organize the brief for the next handoff.", kind: "primary", enabled: true }];
    case "brief_ready":
      return [{ id: "mark_sent", label: "Send to agent", helper: "Send the brief and move to waiting.", kind: "primary", enabled: true }];
    case "waiting_for_agent":
      return [{ id: "receive_result", label: "Receive response", helper: "Bring the agent response back into the workspace.", kind: "primary", enabled: true }];
    case "response_received":
      return [{ id: "request_review", label: "Request review", helper: "Prepare the Critic handoff from the returned draft.", kind: "primary", enabled: true }];
    case "review_requested":
      return [{ id: "mark_sent", label: "Send to agent", helper: "Send the Critic brief and wait for the review.", kind: "primary", enabled: true }];
    case "ready_for_decision":
      return [{ id: "confirm_share", label: "Prepare team share", helper: "Confirm the final share state for Jira and Confluence.", kind: "primary", enabled: true }];
    case "revise":
      return [{ id: "apply_review", label: "Apply review", helper: "Use the review feedback and prepare one more pass.", kind: "primary", enabled: true }];
    case "shared":
      return [{ id: "confirm_share", label: "Check share status", helper: "Review the final shared state.", kind: "primary", enabled: true }];
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
      operatorDecisionLabel: "Revise before team share",
      operatorDecisionDetail: "Use the review feedback to tighten the draft before publishing anything to the team.",
      reviewChecklist: ["Clarify the missing owner.", "Close the schedule dependency.", "Run one more review pass before share."],
    };
  }

  if (state === "shared") {
    return {
      headline: scenario.reviewCopy.sharedHeadline,
      summary: scenario.reviewCopy.sharedSummary,
      outcomeState: "ready_for_decision" as const,
      operatorDecisionLabel: "Shared state confirmed",
      operatorDecisionDetail: "The operator has already confirmed the final share state and the team can now read the result in Jira and Confluence.",
      reviewChecklist: ["Confirm the summary matches across systems.", "Check that the next action is visible.", "Share timing has already been confirmed."],
    };
  }

  return {
    headline: scenario.reviewCopy.readyHeadline,
    summary: scenario.reviewCopy.readySummary,
    outcomeState: "ready_for_decision" as const,
    operatorDecisionLabel: "Operator decision required",
    operatorDecisionDetail: "The Critic review is complete, but the operator still decides whether to share now or revise first.",
    reviewChecklist: ["Check whether the summary is team-ready.", "Confirm Jira and Confluence should show the same message.", "Decide whether to share now or revise once more."],
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
        statusNote = "Waiting for the response from this agent.";
      } else if (isActive && !isWaitingStage && agent.roleId !== "ops") {
        status = "connected";
        statusNote = "This is the active role for the current stage.";
      } else if (agent.roleId === "ops" && (runtime.displayState === "ready_for_decision" || runtime.displayState === "shared")) {
        status = "connected";
        statusNote = "Ready to confirm the final team-share state.";
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
  subtitle: "A connected-agent workspace for continuing project work from shared context.",
  workspaceLabel: "Connected-agent workspace",
  workspaceTagline: "Structured context in, role-based work out, team-sharing state at the end.",
  agents: AGENTS,
  tasks: SCENARIOS.map((scenario) => createTaskRecord(scenario, INITIAL_RUNTIME[scenario.id])),
};
