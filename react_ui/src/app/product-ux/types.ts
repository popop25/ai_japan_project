export type ProductViewId = "task" | "handoff" | "review";

export type AgentRoleId = "pm" | "critic" | "ops";
export type AgentStatus = "connected" | "waiting" | "reviewing";
export type ShareStatusTone = "healthy" | "attention" | "pending";
export type ResultStatusTone = "ready" | "review" | "pending";
export type HandoffMode = "copy_paste" | "file_handoff";
export type TaskActionKind = "primary" | "secondary";

export type TaskDisplayState =
  | "not_started"
  | "brief_ready"
  | "waiting_for_agent"
  | "response_received"
  | "review_requested"
  | "ready_for_decision"
  | "revise"
  | "shared";

export type TaskActionId =
  | "prepare_brief"
  | "mark_sent"
  | "receive_result"
  | "request_review"
  | "apply_review"
  | "confirm_share";

export interface AgentRecord {
  id: string;
  name: string;
  roleId: AgentRoleId;
  roleLabel: string;
  responsibility: string;
  productLabel: string;
  focus: string;
  status: AgentStatus;
  statusNote: string;
}

export interface ConnectedAgentRecord {
  id: string;
  name: string;
  roleId: AgentRoleId;
  roleLabel: string;
  responsibility: string;
  productLabel: string;
  focus: string;
  status: AgentStatus;
  statusNote: string;
}

export interface HandoffModeOption {
  id: HandoffMode;
  label: string;
  helper: string;
}

export interface TaskAction {
  id: TaskActionId;
  label: string;
  helper: string;
  kind: TaskActionKind;
  enabled: boolean;
}

export interface ShareStatus {
  system: string;
  label: string;
  detail: string;
  tone: ShareStatusTone;
  updatedAt: string;
}

export interface ResultItem {
  id: string;
  title: string;
  fromAgentLabel: string;
  summary: string;
  status: ResultStatusTone;
  updatedAt: string;
}

export interface ContextEntry {
  id: string;
  label: string;
  value: string;
}

export interface SourceDocument {
  id: string;
  title: string;
  type: string;
  freshness: string;
  note: string;
}

export interface TaskBriefTemplate {
  roleId: AgentRoleId;
  roleLabel: string;
  title: string;
  instruction: string;
  body: string;
  checklist: string[];
  expectedResponse: string;
  contextIncluded: string[];
  handoffPath: string;
  responsePath: string;
}

export interface TaskRecord {
  id: string;
  isPrimaryDemo: boolean;
  title: string;
  account: string;
  summary: string;
  objective: string;
  dueLabel: string;
  updatedAt: string;
  urgency: string;
  displayState: TaskDisplayState;
  stageLabel: string;
  activeRole: AgentRoleId;
  nextActionLabel: string;
  nextActionDetail: string;
  actions: TaskAction[];
  handoffMode: HandoffMode;
  handoffModeOptions: HandoffModeOption[];
  connectedAgents: ConnectedAgentRecord[];
  activeBrief: TaskBriefTemplate;
  shareStatuses: ShareStatus[];
  results: ResultItem[];
  contextEntries: ContextEntry[];
  sources: SourceDocument[];
  reviewHeadline: string;
  reviewSummary: string;
  reviewChecklist: string[];
  operatorDecisionLabel: string;
  operatorDecisionDetail: string;
  reviewOutcomeState: "ready_for_decision" | "revise";
}

export interface ProductExperience {
  title: string;
  subtitle: string;
  workspaceLabel: string;
  workspaceTagline: string;
  agents: AgentRecord[];
  tasks: TaskRecord[];
}
