import { ProductExperience } from "./types";

export const productExperience: ProductExperience = {
  title: "Connected Agent Workspace",
  subtitle: "프로젝트 맥락을 읽은 내 에이전트가 다음 행동으로 이어서 일하는 작업 공간",
  workspaceLabel: "Tokyo GTM launch prep",
  agents: [
    {
      id: "pm-agent",
      name: "PM Agent",
      role: "요구 정리와 실행 브리프 작성",
      focus: "launch task framing",
      status: "connected",
      connectedSince: "2m ago",
      queueDepth: 2,
      latency: "14s"
    },
    {
      id: "critic-agent",
      name: "Critic",
      role: "리스크와 누락 검토",
      focus: "decision quality",
      status: "reviewing",
      connectedSince: "live",
      queueDepth: 1,
      latency: "28s"
    },
    {
      id: "ops-agent",
      name: "Ops Agent",
      role: "Jira / Confluence 반영",
      focus: "team share sync",
      status: "waiting",
      connectedSince: "ready",
      queueDepth: 0,
      latency: "6s"
    }
  ],
  tasks: [
    {
      id: "task-launch-brief",
      title: "일본 런치 brief 정리",
      account: "AI Japan rollout",
      stage: "Draft in progress",
      summary: "한국 PM 메모와 기존 launch plan을 합쳐 일본 론치용 brief 초안을 만드는 작업입니다.",
      objective: "PM Agent가 바로 읽고 초안을 만들 수 있게 핵심 맥락, 미정 항목, 공유 상태를 한 화면에서 정리합니다.",
      nextActionLabel: "PM 에이전트에 보내기",
      nextActionDetail: "launch timeline, localization open issues, shared-with-team 상태를 포함해 handoff를 보냅니다.",
      dueLabel: "오늘 18:00 KST",
      updatedAt: "5 min ago",
      urgency: "오늘 팀 공유 전 검토 필요",
      agentIds: ["pm-agent", "critic-agent", "ops-agent"],
      handoffTargetId: "pm-agent",
      handoffTitle: "Japan launch brief 초안 요청",
      handoffInstruction: "프로젝트 맥락과 최신 Jira ticket을 읽고, launch goal, open question, next owner를 포함한 1차 brief를 만들어 주세요.",
      reviewHeadline: "Critic이 launch risk 3건을 표시했습니다.",
      reviewSummary: "timeline dependency와 legal copy owner가 비어 있어 팀 공유 전에 수정이 필요합니다.",
      actionLabels: ["PM 에이전트에 보내기", "초안 받기", "Critic에 검토 요청", "검토 결과 반영"],
      shareStatuses: [
        {
          system: "Jira",
          label: "shared with team",
          detail: "LAUNCH-142에 최신 objective 동기화됨",
          tone: "healthy"
        },
        {
          system: "Confluence",
          label: "share update needed",
          detail: "review 반영 후 publish 예정",
          tone: "attention"
        }
      ],
      results: [
        {
          id: "result-brief-v1",
          title: "Brief draft v1",
          fromAgentId: "pm-agent",
          summary: "launch goal, audience, milestones, unresolved owner 포함",
          status: "ready",
          updatedAt: "8 min ago"
        },
        {
          id: "result-critic-v1",
          title: "Critic review",
          fromAgentId: "critic-agent",
          summary: "dependency risk와 team share mismatch 3건 표시",
          status: "review",
          updatedAt: "3 min ago"
        }
      ],
      contextEntries: [
        { id: "ctx-1", label: "Goal", value: "일본 시장용 launch brief를 오늘 안에 공유 가능한 수준으로 정리" },
        { id: "ctx-2", label: "Primary risk", value: "legal review owner와 in-market timeline이 아직 확정되지 않음" },
        { id: "ctx-3", label: "Team expectation", value: "Jira와 Confluence 둘 다 같은 결론으로 업데이트되어야 함" }
      ],
      decisions: [
        { id: "dec-1", label: "launch goal 문구 고정", rationale: "sales deck와 동일한 표현을 유지", state: "locked" },
        { id: "dec-2", label: "legal owner 확인", rationale: "팀 공유 전에 owner 누락 방지", state: "next" },
        { id: "dec-3", label: "Confluence publish timing", rationale: "Critic review 반영 후 공개", state: "watching" }
      ],
      sources: [
        { id: "src-1", title: "Q2 launch narrative", type: "Confluence", freshness: "updated today", note: "시장별 메시지 차이 포함" },
        { id: "src-2", title: "LAUNCH-142", type: "Jira", freshness: "synced 12 min ago", note: "owner, due date, blockers 확인 가능" },
        { id: "src-3", title: "Japan PM notes", type: "Workspace note", freshness: "captured yesterday", note: "현지화 요청과 미정 항목 메모" }
      ]
    },
    {
      id: "task-pricing-check",
      title: "가격 정책 변경 검토",
      account: "Billing update",
      stage: "Waiting for review",
      summary: "가격 변경안이 onboarding flow와 충돌하는지 확인하고 팀 공유용 summary를 준비합니다.",
      objective: "Critic과 Ops Agent까지 연결해 pricing change impact를 빠르게 정리합니다.",
      nextActionLabel: "Critic에 검토 요청",
      nextActionDetail: "impact summary를 검토 보내고 Jira 상태를 shared with team으로 유지합니다.",
      dueLabel: "내일 11:00 JST",
      updatedAt: "16 min ago",
      urgency: "세일즈 FAQ 영향 확인",
      agentIds: ["critic-agent", "ops-agent"],
      handoffTargetId: "critic-agent",
      handoffTitle: "Pricing impact review 요청",
      handoffInstruction: "pricing tier 변경이 onboarding copy, FAQ, sales handoff에 미치는 영향만 압축해서 표시해 주세요.",
      reviewHeadline: "Review 대기 중입니다.",
      reviewSummary: "초안은 준비됐고 Critic의 영향도 점검만 남아 있습니다.",
      actionLabels: ["Critic에 검토 요청", "검토 결과 반영", "팀 공유 상태 확인"],
      shareStatuses: [
        {
          system: "Jira",
          label: "shared with team",
          detail: "BILL-88에 impact note 기록됨",
          tone: "healthy"
        },
        {
          system: "Confluence",
          label: "draft only",
          detail: "FAQ 정리 후 게시 예정",
          tone: "pending"
        }
      ],
      results: [
        {
          id: "result-pricing-summary",
          title: "Impact summary",
          fromAgentId: "pm-agent",
          summary: "FAQ와 trial messaging 변경 포인트 정리",
          status: "ready",
          updatedAt: "20 min ago"
        }
      ],
      contextEntries: [
        { id: "ctx-4", label: "Customer concern", value: "trial 전환 메시지와 세일즈 자료가 동시에 바뀌어야 함" },
        { id: "ctx-5", label: "Open owner", value: "FAQ 문구 승인 담당이 확정되지 않음" }
      ],
      decisions: [
        { id: "dec-4", label: "FAQ 갱신 범위", rationale: "trial과 annual plan만 우선 반영", state: "locked" },
        { id: "dec-5", label: "sales enablement note", rationale: "Confluence publish 전에 별도 정리 필요", state: "next" }
      ],
      sources: [
        { id: "src-4", title: "Pricing proposal", type: "Workspace doc", freshness: "updated 1h ago", note: "변경 배경과 표준 문구" },
        { id: "src-5", title: "BILL-88", type: "Jira", freshness: "synced 20 min ago", note: "approval 흐름 포함" }
      ]
    },
    {
      id: "task-retro-share",
      title: "retro note 팀 공유",
      account: "Post-launch ops",
      stage: "Ready to share",
      summary: "지난주 retro 메모를 에이전트가 읽고 action-oriented summary로 바꾼 뒤 팀에 공유합니다.",
      objective: "action item, owner, next step을 붙인 상태로 Confluence에 남깁니다.",
      nextActionLabel: "검토 결과 반영",
      nextActionDetail: "Critic 코멘트를 정리하고 Confluence를 shared with team 상태로 바꿉니다.",
      dueLabel: "이번 주 금요일",
      updatedAt: "32 min ago",
      urgency: "retro action owner 확정 필요",
      agentIds: ["pm-agent", "ops-agent"],
      handoffTargetId: "ops-agent",
      handoffTitle: "retro summary publish 요청",
      handoffInstruction: "확정된 action item만 남기고 팀이 바로 읽을 수 있는 summary 형식으로 Confluence에 반영해 주세요.",
      reviewHeadline: "publish 가능한 상태입니다.",
      reviewSummary: "minor wording만 정리하면 팀 공유 가능합니다.",
      actionLabels: ["검토 결과 반영", "팀 공유 상태 확인", "Confluence에 반영"],
      shareStatuses: [
        {
          system: "Jira",
          label: "reference only",
          detail: "related ticket 없음",
          tone: "pending"
        },
        {
          system: "Confluence",
          label: "shared with team",
          detail: "retro page 초안 저장됨",
          tone: "healthy"
        }
      ],
      results: [
        {
          id: "result-retro-summary",
          title: "Retro summary",
          fromAgentId: "pm-agent",
          summary: "action item 4건과 owner 제안 포함",
          status: "ready",
          updatedAt: "34 min ago"
        }
      ],
      contextEntries: [
        { id: "ctx-6", label: "Audience", value: "Japan launch squad 전체" },
        { id: "ctx-7", label: "Must keep", value: "실행 가능한 action item만 남기기" }
      ],
      decisions: [
        { id: "dec-6", label: "owner 명시 유지", rationale: "retro가 실행으로 이어지게 하기 위함", state: "locked" }
      ],
      sources: [
        { id: "src-6", title: "Retro raw notes", type: "Workspace note", freshness: "captured last week", note: "발화 원문 포함" },
        { id: "src-7", title: "Retro publish page", type: "Confluence", freshness: "draft saved", note: "final wording만 남음" }
      ]
    }
  ]
};

