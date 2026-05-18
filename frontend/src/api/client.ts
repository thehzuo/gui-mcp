import type {
  LedgerEvent,
  Plan,
  ReviewRecord,
  Run,
  RunStatusSnapshot,
  TaskContract,
  TaskDependency,
  TaskNode,
  ValidationResult
} from "../types/domain";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    },
    ...options
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `${response.status} ${response.statusText}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export const api = {
  listRuns: () => request<Run[]>("/api/runs"),
  createRun: (payload: { name: string; description: string }) =>
    request<Run>("/api/runs", { method: "POST", body: JSON.stringify(payload) }),
  getRun: (runId: string) => request<Run>(`/api/runs/${runId}`),
  cancelRun: (runId: string) => request<Run>(`/api/runs/${runId}/cancel`, { method: "POST" }),
  resumeRun: (runId: string) => request<Run>(`/api/runs/${runId}/resume`, { method: "POST" }),
  pauseRun: (runId: string) => request<Run>(`/api/runs/${runId}/pause`, { method: "POST" }),
  getContract: (runId: string) => request<TaskContract>(`/api/runs/${runId}/contract`),
  saveContract: (runId: string, payload: Omit<TaskContract, "id" | "run_id" | "created_at" | "updated_at">) =>
    request<TaskContract>(`/api/runs/${runId}/contract`, { method: "PUT", body: JSON.stringify(payload) }),
  generatePlan: (runId: string) => request<Plan>(`/api/runs/${runId}/plans/generate`, { method: "POST" }),
  listPlans: (runId: string) => request<Plan[]>(`/api/runs/${runId}/plans`),
  getPlan: (planId: string) => request<Plan>(`/api/plans/${planId}`),
  patchPlan: (planId: string, payload: Partial<Pick<Plan, "summary" | "assumptions" | "open_questions">>) =>
    request<Plan>(`/api/plans/${planId}`, { method: "PATCH", body: JSON.stringify(payload) }),
  validatePlan: (planId: string) => request<ValidationResult>(`/api/plans/${planId}/validate`, { method: "POST" }),
  submitPlanReview: (planId: string) => request<Plan>(`/api/plans/${planId}/submit-review`, { method: "POST" }),
  approvePlan: (planId: string) => request<Plan>(`/api/plans/${planId}/approve`, { method: "POST" }),
  rejectPlan: (planId: string) => request<Plan>(`/api/plans/${planId}/reject`, { method: "POST" }),
  createTask: (planId: string, payload: Partial<TaskNode>) =>
    request<TaskNode>(`/api/plans/${planId}/tasks`, { method: "POST", body: JSON.stringify(payload) }),
  updateTask: (taskId: string, payload: Partial<TaskNode>) =>
    request<TaskNode>(`/api/tasks/${taskId}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteTask: (taskId: string) => request<{ status: string }>(`/api/tasks/${taskId}`, { method: "DELETE" }),
  createDependency: (planId: string, payload: { from_task_id: string; to_task_id: string }) =>
    request<TaskDependency>(`/api/plans/${planId}/dependencies`, { method: "POST", body: JSON.stringify(payload) }),
  deleteDependency: (dependencyId: string) => request<{ status: string }>(`/api/dependencies/${dependencyId}`, { method: "DELETE" }),
  listReviews: (status?: string) => request<ReviewRecord[]>(`/api/reviews${status ? `?status=${status}` : ""}`),
  approveReview: (reviewId: string, comment = "") =>
    request<ReviewRecord>(`/api/reviews/${reviewId}/approve`, { method: "POST", body: JSON.stringify({ reviewer: "local-reviewer", comment }) }),
  rejectReview: (reviewId: string, comment = "") =>
    request<ReviewRecord>(`/api/reviews/${reviewId}/reject`, { method: "POST", body: JSON.stringify({ reviewer: "local-reviewer", comment }) }),
  requestChanges: (reviewId: string, comment = "") =>
    request<ReviewRecord>(`/api/reviews/${reviewId}/request-changes`, { method: "POST", body: JSON.stringify({ reviewer: "local-reviewer", comment }) }),
  startRun: (runId: string) => request<{ status: string; run_id: string }>(`/api/runs/${runId}/start`, { method: "POST" }),
  getStatus: (runId: string) => request<RunStatusSnapshot>(`/api/runs/${runId}/status`),
  getEvents: (runId: string) => request<LedgerEvent[]>(`/api/runs/${runId}/events`)
};

export function streamUrl(runId: string): string {
  return `${API_BASE}/api/runs/${runId}/stream`;
}

