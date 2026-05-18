export type RunStatus =
  | "DRAFT"
  | "PLANNING"
  | "AWAITING_PLAN_REVIEW"
  | "PLAN_APPROVED"
  | "RUNNING"
  | "PAUSED"
  | "COMPLETED"
  | "FAILED"
  | "CANCELED";

export type TaskStatus =
  | "DRAFT"
  | "READY"
  | "BLOCKED"
  | "AWAITING_REVIEW"
  | "APPROVED"
  | "QUEUED"
  | "RUNNING"
  | "VERIFYING"
  | "SUCCEEDED"
  | "FAILED"
  | "NEEDS_HUMAN"
  | "ROLLED_BACK"
  | "CANCELED";

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type Reversibility = "REVERSIBLE" | "PARTIALLY_REVERSIBLE" | "IRREVERSIBLE";
export type AutonomyLevel = "L0" | "L1" | "L2" | "L3" | "L4" | "L5";

export interface Run {
  id: string;
  name: string;
  description: string;
  status: RunStatus;
  active_plan_id: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
  progress_summary: Record<string, number>;
}

export interface TaskContract {
  id: string;
  run_id: string;
  goal: string;
  success_criteria: string[];
  forbidden_losses: string[];
  allowed_tools: string[];
  human_approval_boundaries: string[];
  risk_class: string;
  max_autonomy_level: AutonomyLevel;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface TaskNode {
  id: string;
  run_id: string;
  plan_id: string;
  title: string;
  description: string;
  task_family: string;
  status: TaskStatus;
  review_status: "NOT_REQUIRED" | "PENDING" | "APPROVED" | "REJECTED";
  risk_level: RiskLevel;
  reversibility: Reversibility;
  required_autonomy_level: AutonomyLevel;
  assigned_model_id: string;
  expected_outputs: string[];
  verifier_refs: string[];
  tool_refs: string[];
  executor_type: "mock" | "command";
  executor_config_json: Record<string, unknown>;
  human_review_required: boolean;
  position_x: number;
  position_y: number;
  created_at: string;
  updated_at: string;
}

export interface TaskDependency {
  id: string;
  plan_id: string;
  from_task_id: string;
  to_task_id: string;
  created_at: string;
}

export interface Plan {
  id: string;
  run_id: string;
  version: number;
  status: "DRAFT" | "AWAITING_REVIEW" | "APPROVED" | "LOCKED" | "SUPERSEDED" | "REJECTED";
  summary: string;
  assumptions: string[];
  open_questions: string[];
  created_by: string;
  approved_by: string | null;
  approved_at: string | null;
  locked_at: string | null;
  created_at: string;
  updated_at: string;
  tasks: TaskNode[];
  dependencies: TaskDependency[];
}

export interface ReviewRecord {
  id: string;
  run_id: string;
  plan_id: string | null;
  task_id: string | null;
  review_type: "PLAN_REVIEW" | "TASK_REVIEW" | "HUMAN_OVERRIDE";
  status: "PENDING" | "APPROVED" | "REJECTED" | "CHANGES_REQUESTED";
  reviewer: string | null;
  decision: string | null;
  comment: string;
  reason: string;
  packet_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface LedgerEvent {
  id: string;
  run_id: string;
  plan_id: string | null;
  task_id: string | null;
  event_type: string;
  payload_json: Record<string, unknown>;
  created_at: string;
  created_by: string;
}

export interface VerificationResult {
  id: string;
  task_id: string;
  run_id: string;
  verifier_name: string;
  status: "PASS" | "FAIL" | "UNKNOWN" | "SKIPPED";
  score: number | null;
  summary: string;
  evidence_json: Record<string, unknown>;
  created_at: string;
}

export interface RunStatusSnapshot {
  run: Run;
  plan: Plan | null;
  reviews: ReviewRecord[];
  verification_results: VerificationResult[];
  events: LedgerEvent[];
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

