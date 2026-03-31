export type ProductViewId = "workboard" | "task" | "handoff" | "review" | "context";

export type AgentStatus = "connected" | "waiting" | "reviewing";
export type ShareStatusTone = "healthy" | "attention" | "pending";
export type ResultStatusTone = "ready" | "review" | "pending";

export interface AgentRecord {
  id: string;
  name: string;
  role: string;
  focus: string;
  status: AgentStatus;
  connectedSince: string;
  queueDepth: number;
  latency: string;
}

export interface ShareStatus {
  system: string;
  label: string;
  detail: string;
  tone: ShareStatusTone;
}

export interface ResultItem {
  id: string;
  title: string;
  fromAgentId: string;
  summary: string;
  status: ResultStatusTone;
  updatedAt: string;
}

export interface ContextEntry {
  id: string;
  label: string;
  value: string;
}

export interface DecisionItem {
  id: string;
  label: string;
  rationale: string;
  state: "locked" | "watching" | "next";
}

export interface SourceDocument {
  id: string;
  title: string;
  type: string;
  freshness: string;
  note: string;
}

export interface TaskRecord {
  id: string;
  title: string;
  account: string;
  stage: string;
  summary: string;
  objective: string;
  nextActionLabel: string;
  nextActionDetail: string;
  dueLabel: string;
  updatedAt: string;
  urgency: string;
  agentIds: string[];
  handoffTargetId: string;
  handoffTitle: string;
  handoffInstruction: string;
  reviewHeadline: string;
  reviewSummary: string;
  actionLabels: string[];
  shareStatuses: ShareStatus[];
  results: ResultItem[];
  contextEntries: ContextEntry[];
  decisions: DecisionItem[];
  sources: SourceDocument[];
}

export interface ProductExperience {
  title: string;
  subtitle: string;
  workspaceLabel: string;
  agents: AgentRecord[];
  tasks: TaskRecord[];
}

