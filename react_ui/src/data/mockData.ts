import { ProductData } from "../types";

export const productData: ProductData = {
  overview: {
    name: "AI Japan Project",
    purpose: "Operate external AI work through a clear control plane instead of a fragile chat trail.",
    customer: "Japan Retail DX Program",
    currentStage: "React UI spike against the live harness baseline",
    activeWork: "Revision loop for the store inquiry assistant requirements draft",
    lastUpdated: "March 30, 2026",
    modeLabel: "Hybrid harness",
    modeDetail: "Streamlit stays live; React models the next product surface",
    nextActionTitle: "Regenerate the PM packet with measurable rollout metrics",
    nextActionBody:
      "Critic flagged missing success criteria, store-manager exception paths, and publish conditions. The operator should reissue the PM packet, receive the revised markdown, and only then request final review.",
  },
  connections: [
    {
      id: "jira",
      name: "Jira task sync",
      description: "Canonical task source with localized status mapping already hardened in the harness.",
      status: "connected",
      lastSync: "2 min ago",
    },
    {
      id: "confluence",
      name: "Confluence context and artifact sync",
      description: "Narrative context and approved outputs stay readable outside the app.",
      status: "connected",
      lastSync: "4 min ago",
    },
    {
      id: "handoff",
      name: "External agent handoff",
      description: "Manual chat, file handoff, or split PM and Critic threads remain first-class flows.",
      status: "connected",
      lastSync: "Packet files ready",
    },
    {
      id: "runtime",
      name: "Local run ledger",
      description: "Prompt packets and receipts continue to live under project/runs for auditability.",
      status: "connected",
      lastSync: "Updated on every ingest",
    },
  ],
  metrics: [
    {
      label: "Active workflows",
      value: "3",
      detail: "Two drafts are moving forward and one is back in a revision loop after Critic feedback.",
    },
    {
      label: "Operator decisions",
      value: "2",
      detail: "These items require a human decision rather than another model response.",
    },
    {
      label: "Artifacts ready",
      value: "5",
      detail: "Latest drafts and reviews are already linked back to task history and source systems.",
    },
    {
      label: "System health",
      value: "100%",
      detail: "Local packet runtime, Jira sync, and Confluence sync are all healthy in the current baseline.",
    },
  ],
  queue: [
    {
      id: "task_store_inquiry",
      title: "Store inquiry assistant requirements draft",
      jiraKey: "AJP-204",
      status: "revision_needed",
      stage: "Revision loop",
      owner: "Ops program lead",
      nextAction: "Regenerate the PM packet with acceptance metrics and exception handling.",
      updatedAt: "11:18 KST",
      artifactCount: 2,
    },
    {
      id: "task_runbook",
      title: "Operator runbook packaging",
      jiraKey: "AJP-205",
      status: "in_progress",
      stage: "Critic handoff",
      owner: "Program manager",
      nextAction: "Paste the returned Critic review into the harness and decide whether to publish.",
      updatedAt: "10:42 KST",
      artifactCount: 1,
    },
    {
      id: "task_exec_brief",
      title: "Executive steering brief",
      jiraKey: "AJP-199",
      status: "review_requested",
      stage: "Share and align",
      owner: "Business sponsor",
      nextAction: "Review the latest artifact and distribute the approved narrative.",
      updatedAt: "Yesterday",
      artifactCount: 2,
    },
  ],
  activity: [
    {
      time: "11:18 KST",
      title: "Critic review ingested for AJP-204",
      detail: "The review returned a revise verdict and surfaced missing rollout metrics plus store-manager exception handling.",
      status: "revision_needed",
    },
    {
      time: "11:02 KST",
      title: "Critic packet generated",
      detail: "The packet linked the PM draft, context markdown, and review contract before handoff.",
      status: "in_progress",
    },
    {
      time: "10:48 KST",
      title: "PM draft synced to Confluence",
      detail: "The latest markdown artifact is visible to stakeholders without reopening the agent thread.",
      status: "in_progress",
    },
    {
      time: "10:11 KST",
      title: "PM draft ingested",
      detail: "Returned markdown was stored as the canonical artifact and linked back to Jira task AJP-204.",
      status: "in_progress",
    },
    {
      time: "09:54 KST",
      title: "Context refresh completed",
      detail: "The current stage, audience, guardrails, and next actions were refreshed before packet generation.",
      status: "done",
    },
  ],
  projectGraph: [
    { label: "W1", scope: 18, started: 4, completed: 2 },
    { label: "W2", scope: 20, started: 8, completed: 5 },
    { label: "W3", scope: 21, started: 11, completed: 8 },
    { label: "W4", scope: 21, started: 14, completed: 10 },
    { label: "W5", scope: 22, started: 16, completed: 12 },
  ],
  contextDocument: [
    {
      id: "why",
      title: "Why this harness exists",
      summary: "The product is not a chat window. It is an operating surface for AI work with memory, traceability, and explicit control.",
      paragraphs: [
        "The core promise is that a non-technical operator can move AI work forward without becoming the system integrator. Context, tasks, packets, artifacts, and sync stay inside the harness even when the reasoning happens in Codex or Claude.",
        "That separation matters because the execution agent can change, but the operating model should remain stable. The product must feel trustworthy enough for business teams to run repeatable work, not just demo a clever prompt.",
      ],
      bullets: [
        "Context stays canonical and readable.",
        "Workflow state stays explicit.",
        "Artifacts stay reviewable outside the agent thread.",
      ],
    },
    {
      id: "operator",
      title: "What the operator owns",
      summary: "The operator curates context, starts workflows, chooses the next step, and approves the final output.",
      paragraphs: [
        "The UI should keep decision points visible: what changed, what is blocked, and what happens next. The product should never imply that AI quietly handled the work on its own.",
        "Packet generation, handoff, and ingest are all deliberate actions. That makes the system auditable and keeps responsibility anchored to the human operator.",
      ],
      bullets: [
        "Review context before dispatch.",
        "Choose how the packet is handed off.",
        "Accept or reject review outcomes before publish.",
      ],
    },
    {
      id: "guardrails",
      title: "Guardrails and constraints",
      summary: "The current backend already supports local and Atlassian modes. The React surface should respect those boundaries instead of rewriting them.",
      paragraphs: [
        "Prompt packets and run traces remain local in both modes. Jira and Confluence become canonical only where the current service layer already says they are.",
        "The Critic review contract is intentionally rigid: verdict, summary, missing items, and recommended changes must remain parseable so the viewer stays trustworthy.",
      ],
      bullets: [
        "Do not move orchestration logic into the frontend.",
        "Preserve markdown-first packets and artifacts.",
        "Treat external agent handoff as a first-class feature.",
      ],
    },
    {
      id: "workflow",
      title: "Workflow expectation",
      summary: "Every workflow should read like a guided operating procedure rather than a pile of forms.",
      paragraphs: [
        "The UI needs to tell the operator what step they are in, why that step exists, and what becomes possible after it completes. That is the difference between a control plane and a generic dashboard.",
        "Document-shaped information and workflow-shaped information should live together. The operator should never have to jump to another product just to understand the state of the work.",
      ],
      bullets: [
        "State, action, and connected context should appear together.",
        "The default read should be summary-first.",
        "Metadata should support the workflow instead of leading it.",
      ],
    },
    {
      id: "success",
      title: "Success signal for this spike",
      summary: "Someone seeing the React surface for the first time should immediately understand that AI work is being operated, not merely chatted with.",
      paragraphs: [
        "This spike is successful if it establishes a convincing shell, reusable visual tokens, and enough screen patterns to guide the next implementation phase. It does not need to replace Streamlit today.",
      ],
      bullets: [
        "Show a stable design system direction.",
        "Preserve the current workflow contract.",
        "Clarify the backend seam for a future API.",
      ],
    },
  ],
  contextFields: [
    { label: "Audience", value: "Non-technical operator running AI work as a controlled workflow" },
    { label: "Canonical task source", value: "Jira in Atlassian mode, local YAML in demo mode" },
    { label: "Canonical context source", value: "Confluence or project/03_context.md depending on runtime mode" },
    { label: "Artifact contract", value: "Markdown draft plus Critic YAML frontmatter" },
    { label: "Agent posture", value: "External PM and Critic teammates rather than embedded copilots" },
    { label: "Primary message", value: "The operator runs the workflow and decides when work is ready" },
  ],
  decisions: [
    {
      date: "2026-03-28",
      title: "Requirements draft remains the first deliverable",
      reason: "It is the fastest artifact for stakeholders to review and the clearest way to prove controlled AI work in the PoC.",
    },
    {
      date: "2026-03-28",
      title: "Prompt packets stay markdown-first",
      reason: "That keeps handoff agent-neutral and preserves today\'s local runtime traceability.",
    },
    {
      date: "2026-03-29",
      title: "Critic remains a business review gate, not a silent validator",
      reason: "The product should show why the draft is ready or not ready in language an operator can act on.",
    },
    {
      date: "2026-03-30",
      title: "React spike focuses on shell and information architecture",
      reason: "The goal is to set the product direction without rewriting the existing Python orchestration layer.",
    },
  ],
  workflow: {
    title: "Store inquiry assistant requirements draft",
    headline: "A guided revision loop that treats PM and Critic as external teammates, not embedded assistants.",
    subtitle:
      "The workflow surface keeps the operator in control of packet generation, handoff, ingest, and approval while preserving the same service-layer contracts that already exist in Python.",
    currentTaskId: "AJP-204",
    currentStatus: "revision_needed",
    steps: [
      {
        id: "context-lock",
        title: "Context checkpoint",
        detail: "Confirm customer, current stage, guardrails, and references before packet generation.",
        status: "done",
        operatorAction: "Context was refreshed and accepted before the task moved forward.",
        outcome: "Packet generation is grounded in current context.",
      },
      {
        id: "pm-packet",
        title: "PM packet",
        detail: "Generate a structured brief for the external PM agent.",
        status: "done",
        operatorAction: "Packet v3 was created and stored under project/runs.",
        outcome: "Ready for manual or file handoff.",
      },
      {
        id: "pm-ingest",
        title: "PM draft ingest",
        detail: "Capture the returned markdown artifact and link it back to the task.",
        status: "done",
        operatorAction: "The returned draft was stored as the canonical PM artifact.",
        outcome: "The workflow can now move to Critic review.",
      },
      {
        id: "critic-packet",
        title: "Critic packet",
        detail: "Ask for a review with verdict, missing items, and recommended changes.",
        status: "done",
        operatorAction: "The Critic packet referenced the draft, context, and review contract.",
        outcome: "The review came back in a parseable markdown format.",
      },
      {
        id: "critic-review",
        title: "Critic review",
        detail: "Surface verdict, gaps, and recommendations for the operator.",
        status: "done",
        operatorAction: "The revise verdict was ingested and summarized.",
        outcome: "The missing rollout metrics and exception paths are now explicit.",
      },
      {
        id: "revision-loop",
        title: "Revision loop",
        detail: "Re-issue the PM packet with explicit fixes before sign-off.",
        status: "current",
        operatorAction: "Regenerate the PM packet with success metrics and store-manager edge cases.",
        outcome: "An approved draft can then sync cleanly to Jira and Confluence.",
      },
    ],
    packet: {
      title: "PM Revision Packet / Store Inquiry Assistant",
      audience: "External PM agent such as Codex or Claude",
      handoffMode: "File handoff preferred",
      objective: "Close the gaps surfaced by Critic without rewriting the whole draft or changing the workflow contract.",
      inputs: [
        "Current context markdown and decisions log",
        "Latest PM draft already stored as the canonical artifact",
        "Critic verdict, missing items, and recommended changes",
      ],
      outputContract: [
        "Return markdown only",
        "Preserve the requirements-draft structure",
        "Add measurable success criteria and exception handling",
        "State publish readiness conditions for the operator",
      ],
      snippet: "## Mission\nRevise the existing requirements draft for the store inquiry assistant.\n\n## Required changes\n- Add measurable rollout metrics by channel and resolution time.\n- Describe how store managers escalate ambiguous requests.\n- Clarify what conditions must be true before the draft is ready for stakeholder sign-off.\n\n## Output rules\nReturn only the revised markdown document.",
    },
    handoffModes: [
      {
        name: "Manual chat handoff",
        summary: "Fastest path when the operator is already working in an existing Codex or Claude chat.",
        fit: "Best for speed and low setup cost.",
      },
      {
        name: "File handoff",
        summary: "Pass the packet path under project/runs directly to the agent and keep the packet canonical.",
        fit: "Best fit for the future desktop workflow and strongest audit trail.",
      },
      {
        name: "Split PM and Critic threads",
        summary: "Keep separate specialized agents and reconcile both outputs through the harness.",
        fit: "Matches the current role-based model without forcing a single chat surface.",
      },
    ],
    runTrace: [
      {
        time: "09:54",
        label: "Context updated",
        detail: "Customer, stage, next actions, and decisions were refreshed before work started.",
        status: "done",
      },
      {
        time: "10:01",
        label: "PM packet generated",
        detail: "The first packet was written to project/runs and linked to AJP-204.",
        status: "done",
      },
      {
        time: "10:11",
        label: "PM draft ingested",
        detail: "Returned markdown became the active artifact and triggered the next workflow stage.",
        status: "in_progress",
      },
      {
        time: "11:02",
        label: "Critic packet generated",
        detail: "The review request carried the PM artifact plus context references.",
        status: "done",
      },
      {
        time: "11:18",
        label: "Critic verdict received",
        detail: "The review was parsed as revise with actionable missing items.",
        status: "revision_needed",
      },
      {
        time: "Now",
        label: "Awaiting operator revision dispatch",
        detail: "The workflow is blocked until the operator regenerates the PM packet.",
        status: "revision_needed",
      },
    ],
    checklists: [
      {
        title: "Operator checklist",
        items: [
          "Confirm the missing metrics and exception paths are still the right scope.",
          "Regenerate the PM packet without mutating the task identity.",
          "Hand the packet to the external PM agent and ingest the revised markdown.",
          "Request a final Critic review only after the new draft is stored.",
        ],
      },
      {
        title: "What the backend already guarantees",
        items: [
          "Task state transitions stay in the ProjectService boundary.",
          "Prompt packets and run receipts stay local for auditability.",
          "Atlassian sync rules remain mode-aware and fail closed when trust is unclear.",
          "Critic markdown stays parseable through the existing frontmatter contract.",
        ],
      },
    ],
    syncPreview: [
      {
        label: "Task state",
        target: "Jira / AJP-204",
        detail: "Update workflow status and keep linked artifact references aligned after approval.",
        status: "connected",
      },
      {
        label: "Context source",
        target: "Confluence context page",
        detail: "Refresh the current-stage narrative only when the operator accepts the new state.",
        status: "connected",
      },
      {
        label: "Artifact record",
        target: "Confluence artifact page",
        detail: "Store the approved draft and review so stakeholders can read them without the agent thread.",
        status: "connected",
      },
    ],
  },
  artifacts: [
    {
      id: "artifact_pm_store_inquiry_v3",
      title: "Store Inquiry Assistant Requirements Draft",
      kind: "pm_output",
      status: "revision_needed",
      summary:
        "The draft explains the operational problem clearly and lays out the workflow, but it still lacks measurable rollout criteria and store-manager exception handling.",
      updatedAt: "Today, 11:08",
      linkedTask: "AJP-204",
      externalLinks: [
        { label: "AJP-204", system: "Jira", href: "https://jira.example.com/browse/AJP-204" },
        { label: "Requirements Draft Page", system: "Confluence", href: "https://confluence.example.com/wiki/spaces/AJP/pages/204" },
      ],
      callouts: [
        "Add acceptance metrics by channel and time-to-resolution.",
        "Clarify how store managers escalate ambiguous requests.",
        "State publish readiness conditions for non-technical operators.",
      ],
      sections: [
        {
          id: "pm-background",
          title: "Background",
          summary: "The draft anchors the workflow in repeated store inquiries that currently depend on manual routing.",
          paragraphs: [
            "The proposed assistant is meant to reduce the load on store teams by turning recurring inquiries into a consistent workflow rather than an ad hoc response pattern.",
          ],
        },
        {
          id: "pm-workflow",
          title: "Workflow shape",
          summary: "The draft already describes intake, triage, and operator approval as separate responsibilities.",
          paragraphs: [
            "The assistant should route routine requests automatically, surface ambiguous cases for human review, and preserve a visible operating history for every task.",
          ],
          bullets: [
            "Intake and categorization",
            "Suggested next action for the operator",
            "Escalation path for ambiguous requests",
          ],
        },
        {
          id: "pm-functional",
          title: "Functional requirements",
          summary: "Core requirements exist, but they are not yet tied to measurable rollout targets.",
          paragraphs: [
            "The system must preserve context, generate packets, capture returned artifacts, and sync the accepted state to external systems. The missing piece is how the operator decides the workflow is truly ready to scale.",
          ],
        },
        {
          id: "pm-gap",
          title: "Open gap",
          summary: "The draft still leaves publish readiness subjective.",
          paragraphs: [
            "Without metrics and exception handling, the operator can read the narrative but cannot make a confident go or no-go decision.",
          ],
        },
      ],
    },
    {
      id: "artifact_critic_store_inquiry_v1",
      title: "Critic Review / Store Inquiry Assistant",
      kind: "critic_review",
      status: "revision_needed",
      summary:
        "Clear structure and strong narrative, but the operator still cannot judge rollout readiness because success criteria and exception paths are missing.",
      updatedAt: "Today, 11:18",
      linkedTask: "AJP-204",
      verdict: "revise",
      externalLinks: [
        { label: "AJP-204", system: "Jira", href: "https://jira.example.com/browse/AJP-204" },
        { label: "Critic Review Page", system: "Confluence", href: "https://confluence.example.com/wiki/spaces/AJP/pages/205" },
      ],
      callouts: [
        "No measurable success metrics are defined.",
        "Store-manager exception handling is underspecified.",
        "Publish readiness is still based on judgment rather than explicit conditions.",
      ],
      sections: [
        {
          id: "critic-verdict",
          title: "Verdict",
          summary: "Revise before publish.",
          paragraphs: [
            "The current draft is coherent and readable, but it does not yet support a confident business decision about rollout readiness.",
          ],
        },
        {
          id: "critic-missing",
          title: "Missing items",
          summary: "The review focuses on concrete operator-facing gaps rather than abstract writing quality.",
          paragraphs: [
            "The operator still needs success metrics, exception handling, and unambiguous publish conditions before the workflow can be considered controlled.",
          ],
          bullets: [
            "Success criteria by channel and response window",
            "Escalation path for ambiguous or multi-store issues",
            "Explicit publish readiness checklist",
          ],
        },
        {
          id: "critic-recommendations",
          title: "Recommended changes",
          summary: "The next PM packet should focus on targeted repair, not a full rewrite.",
          paragraphs: [
            "The best move is to preserve the existing structure and tighten the sections that let an operator judge whether the draft is ready for stakeholder sign-off.",
          ],
        },
      ],
    },
    {
      id: "artifact_context_snapshot",
      title: "Context Snapshot / AI Japan Project",
      kind: "context_snapshot",
      status: "done",
      summary:
        "A narrative source of truth that keeps project purpose, audience, guardrails, and next actions aligned across local and Atlassian modes.",
      updatedAt: "Today, 09:30",
      linkedTask: "Program",
      externalLinks: [
        { label: "Context Page", system: "Confluence", href: "https://confluence.example.com/wiki/spaces/AJP/pages/context" },
      ],
      callouts: [
        "The context file should stay readable to non-developers.",
        "Structured fields and narrative context must remain in sync.",
        "Next actions should read like operating guidance, not metadata.",
      ],
      sections: [
        {
          id: "context-summary",
          title: "Executive summary",
          summary: "The program validates whether business teams can operate AI workflows through a guided harness.",
          paragraphs: [
            "The spike focuses on a control plane where context, workflow, and artifacts read as one product surface rather than a series of disconnected tools.",
          ],
        },
        {
          id: "context-stage",
          title: "Current stage",
          summary: "The live harness is operational; the current job is to define the next UI standard.",
          paragraphs: [
            "The Streamlit shell remains the working product today. This React spike establishes the design system and screen patterns for a later transition.",
          ],
        },
        {
          id: "context-actions",
          title: "Next actions",
          summary: "The highest-priority work is to make the requirements workflow clearer and more trustworthy for operators.",
          paragraphs: [
            "That means the first read must show current situation, next action, connected systems, and the most recent artifact without forcing the user to decipher raw metadata.",
          ],
        },
      ],
    },
  ],
  apiBoundaries: [
    {
      method: "GET",
      path: "/api/overview",
      purpose: "Return the dashboard briefing: context summary, next action, counters, queue, activity, and connection state.",
      notes: "This is the shell-level endpoint the React app needs on first load.",
    },
    {
      method: "GET",
      path: "/api/context",
      purpose: "Return canonical structured context plus rendered markdown sections for the context workspace.",
      notes: "Keep the backend responsible for merging local and Atlassian sources.",
    },
    {
      method: "PATCH",
      path: "/api/context",
      purpose: "Persist edited context fields and regenerate the markdown representation in one operation.",
      notes: "The frontend should not render the canonical markdown on its own.",
    },
    {
      method: "GET",
      path: "/api/tasks/:taskId/workflow",
      purpose: "Return task detail, packets, artifacts, review summary, and current guided step information.",
      notes: "This is the React equivalent of the current TaskDetail view model.",
    },
    {
      method: "POST",
      path: "/api/tasks/:taskId/workflow/actions",
      purpose: "Dispatch PM or Critic packets and ingest returned markdown results using explicit action types.",
      notes: "Keep state transitions inside the service layer rather than the client.",
    },
    {
      method: "GET",
      path: "/api/artifacts/:artifactId",
      purpose: "Return summary-first artifact content, review metadata, and linked Jira or Confluence references.",
      notes: "Supports the artifact viewer without forcing raw markdown to be the first render.",
    },
  ],
};
