import type { LedgerEvent, Plan, ReviewRecord, Run, RunStatusSnapshot, TaskContract, TaskNode, VerificationResult } from "../types/domain";

export const runFixture: Run = {
  id: "run-1",
  name: "Build DAG execution backend",
  description: "Implement a reviewed task DAG and execution dashboard.",
  status: "RUNNING",
  active_plan_id: "plan-1",
  created_by: "local-user",
  created_at: "2026-05-18T00:00:00Z",
  updated_at: "2026-05-18T00:00:00Z",
  progress_summary: { SUCCEEDED: 2, AWAITING_REVIEW: 1 }
};

export const contractFixture: TaskContract = {
  id: "contract-1",
  run_id: "run-1",
  goal: "Build backend support for task DAG execution.",
  success_criteria: ["DAG can be created through API.", "Cycles are rejected."],
  forbidden_losses: ["Do not delete existing tables."],
  allowed_tools: ["mock_executor", "command_executor", "test_runner"],
  human_approval_boundaries: ["before_plan_execution"],
  risk_class: "MEDIUM",
  max_autonomy_level: "L3",
  notes: "",
  created_at: "2026-05-18T00:00:00Z",
  updated_at: "2026-05-18T00:00:00Z"
};

export const taskFixtures: TaskNode[] = [
  {
    id: "task-1",
    run_id: "run-1",
    plan_id: "plan-1",
    title: "Inspect current mission boundary",
    description: "Review the Task Contract goal and constraints.",
    task_family: "code_analysis",
    status: "SUCCEEDED",
    review_status: "NOT_REQUIRED",
    risk_level: "LOW",
    reversibility: "REVERSIBLE",
    required_autonomy_level: "L3",
    assigned_model_id: "local-default",
    expected_outputs: ["Mission boundary notes"],
    verifier_refs: ["command_exit_code"],
    tool_refs: ["mock_executor"],
    executor_type: "mock",
    executor_config_json: {},
    human_review_required: false,
    position_x: 0,
    position_y: 80,
    created_at: "2026-05-18T00:00:00Z",
    updated_at: "2026-05-18T00:00:00Z"
  },
  {
    id: "task-2",
    run_id: "run-1",
    plan_id: "plan-1",
    title: "Review risky boundary",
    description: "Human confirms that the work remains inside the approved mission boundary.",
    task_family: "deployment",
    status: "AWAITING_REVIEW",
    review_status: "PENDING",
    risk_level: "HIGH",
    reversibility: "PARTIALLY_REVERSIBLE",
    required_autonomy_level: "L3",
    assigned_model_id: "local-default",
    expected_outputs: ["Human approval decision"],
    verifier_refs: ["noop"],
    tool_refs: ["mock_executor"],
    executor_type: "mock",
    executor_config_json: {},
    human_review_required: true,
    position_x: 360,
    position_y: 80,
    created_at: "2026-05-18T00:00:00Z",
    updated_at: "2026-05-18T00:00:00Z"
  }
];

export const planFixture: Plan = {
  id: "plan-1",
  run_id: "run-1",
  version: 1,
  status: "DRAFT",
  summary: "Template plan generated from the Task Contract.",
  assumptions: ["Local trusted execution"],
  open_questions: [],
  created_by: "template_planner",
  approved_by: null,
  approved_at: null,
  locked_at: null,
  created_at: "2026-05-18T00:00:00Z",
  updated_at: "2026-05-18T00:00:00Z",
  tasks: taskFixtures,
  dependencies: [{ id: "dep-1", plan_id: "plan-1", from_task_id: "task-1", to_task_id: "task-2", created_at: "2026-05-18T00:00:00Z" }]
};

export const reviewFixture: ReviewRecord = {
  id: "review-1",
  run_id: "run-1",
  plan_id: "plan-1",
  task_id: "task-2",
  review_type: "TASK_REVIEW",
  status: "PENDING",
  reviewer: null,
  decision: null,
  comment: "",
  reason: "Task is high risk and verifier strength is NONE.",
  packet_json: {
    task_title: "Review risky boundary",
    why_review_is_required: "Task is high risk and verifier strength is NONE.",
    risk_level: "HIGH",
    verifier_coverage: "NONE",
    recommended_decision: "Approve if the task remains inside the Task Contract boundaries."
  },
  created_at: "2026-05-18T00:00:00Z",
  updated_at: "2026-05-18T00:00:00Z"
};

export const eventFixture: LedgerEvent = {
  id: "event-1",
  run_id: "run-1",
  plan_id: "plan-1",
  task_id: "task-2",
  event_type: "TASK_REVIEW_REQUESTED",
  payload_json: {},
  created_at: "2026-05-18T00:00:00Z",
  created_by: "system"
};

export const verifierFixture: VerificationResult = {
  id: "verification-1",
  task_id: "task-1",
  run_id: "run-1",
  verifier_name: "command_exit_code",
  status: "PASS",
  score: 1,
  summary: "Command completed with exit code 0.",
  evidence_json: { exit_code: 0 },
  created_at: "2026-05-18T00:00:00Z"
};

export const statusFixture: RunStatusSnapshot = {
  run: runFixture,
  plan: { ...planFixture, status: "LOCKED" },
  reviews: [reviewFixture],
  verification_results: [verifierFixture],
  events: [eventFixture]
};

