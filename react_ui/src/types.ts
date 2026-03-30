export type ViewId = "dashboard" | "context" | "workflow" | "artifacts";
export type WorkflowStatus = "pending" | "in_progress" | "review_requested" | "revision_needed" | "done";
export type ConnectionStatus = "connected" | "degraded" | "pending";
export type ArtifactKind = "pm_output" | "critic_review" | "context_snapshot";
export type StepStatus = "done" | "current" | "upcoming";

export interface LinkRef {
  label: string;
  system: string;
  href: string;
}

export interface ProjectOverview {
  name: string;
  purpose: string;
  customer: string;
  currentStage: string;
  activeWork: string;
  lastUpdated: string;
  modeLabel: string;
  modeDetail: string;
  nextActionTitle: string;
  nextActionBody: string;
}

export interface Connection {
  id: string;
  name: string;
  description: string;
  status: ConnectionStatus;
  lastSync: string;
}

export interface Metric {
  label: string;
  value: string;
  detail: string;
}

export interface QueueItem {
  id: string;
  title: string;
  jiraKey: string;
  status: WorkflowStatus;
  stage: string;
  owner: string;
  nextAction: string;
  updatedAt: string;
  artifactCount: number;
}

export interface ActivityItem {
  time: string;
  title: string;
  detail: string;
  status: WorkflowStatus;
}

export interface ProjectGraphPoint {
  label: string;
  scope: number;
  started: number;
  completed: number;
}

export interface DocumentSection {
  id: string;
  title: string;
  summary: string;
  paragraphs: string[];
  bullets?: string[];
}

export interface ContextField {
  label: string;
  value: string;
}

export interface DecisionItem {
  date: string;
  title: string;
  reason: string;
}

export interface WorkflowStep {
  id: string;
  title: string;
  detail: string;
  status: StepStatus;
  operatorAction: string;
  outcome: string;
}

export interface PacketPreview {
  title: string;
  audience: string;
  handoffMode: string;
  objective: string;
  inputs: string[];
  outputContract: string[];
  snippet: string;
}

export interface HandoffMode {
  name: string;
  summary: string;
  fit: string;
}

export interface RunTraceItem {
  time: string;
  label: string;
  detail: string;
  status: WorkflowStatus;
}

export interface ChecklistBlock {
  title: string;
  items: string[];
}

export interface SyncPreviewItem {
  label: string;
  target: string;
  detail: string;
  status: ConnectionStatus;
}

export interface WorkflowWorkspaceData {
  title: string;
  headline: string;
  subtitle: string;
  currentTaskId: string;
  currentStatus: WorkflowStatus;
  steps: WorkflowStep[];
  packet: PacketPreview;
  handoffModes: HandoffMode[];
  runTrace: RunTraceItem[];
  checklists: ChecklistBlock[];
  syncPreview: SyncPreviewItem[];
}

export interface ArtifactItem {
  id: string;
  title: string;
  kind: ArtifactKind;
  status: WorkflowStatus;
  summary: string;
  updatedAt: string;
  linkedTask: string;
  verdict?: "approve" | "revise";
  externalLinks: LinkRef[];
  sections: DocumentSection[];
  callouts: string[];
}

export interface ApiBoundary {
  method: "GET" | "POST" | "PATCH";
  path: string;
  purpose: string;
  notes: string;
}

export interface ProductData {
  overview: ProjectOverview;
  connections: Connection[];
  metrics: Metric[];
  queue: QueueItem[];
  activity: ActivityItem[];
  projectGraph: ProjectGraphPoint[];
  contextDocument: DocumentSection[];
  contextFields: ContextField[];
  decisions: DecisionItem[];
  workflow: WorkflowWorkspaceData;
  artifacts: ArtifactItem[];
  apiBoundaries: ApiBoundary[];
}
