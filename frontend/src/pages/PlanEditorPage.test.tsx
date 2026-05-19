import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { planFixture, taskFixtures } from "../test/fixtures";
import { renderRoute } from "../test/test-utils";
import { PlanEditorPage } from "./PlanEditorPage";

const apiMock = vi.hoisted(() => ({
  listPlans: vi.fn(),
  getPlan: vi.fn(),
  validatePlan: vi.fn(),
  submitPlanReview: vi.fn(),
  approvePlan: vi.fn(),
  rejectPlan: vi.fn(),
  revisePlan: vi.fn(),
  createTask: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
  createDependency: vi.fn(),
  deleteDependency: vi.fn()
}));

vi.mock("../api/client", () => ({ api: apiMock }));

vi.mock("../components/DagCanvas", () => ({
  DagCanvas: ({ plan, onConnect, onMoveTask }: { plan: typeof planFixture; onConnect: (from: string, to: string) => void; onMoveTask: (id: string, x: number, y: number) => void }) => (
    <div>
      <div>DAG mock {plan.tasks.length}</div>
      <button onClick={() => onConnect("task-1", "task-2")}>Connect Tasks</button>
      <button onClick={() => onMoveTask("task-1", 10, 20)}>Move Task</button>
    </div>
  )
}));

describe("PlanEditorPage", () => {
  beforeEach(() => {
    apiMock.listPlans.mockResolvedValue([planFixture]);
    apiMock.getPlan.mockResolvedValue(planFixture);
    apiMock.validatePlan.mockResolvedValue({ valid: true, errors: [], warnings: [] });
    apiMock.submitPlanReview.mockResolvedValue({ ...planFixture, status: "AWAITING_REVIEW" });
    apiMock.approvePlan.mockResolvedValue({ ...planFixture, status: "LOCKED" });
    apiMock.rejectPlan.mockResolvedValue({ ...planFixture, status: "REJECTED" });
    apiMock.revisePlan.mockResolvedValue({ ...planFixture, id: "plan-2", version: 2, status: "DRAFT" });
    apiMock.createTask.mockResolvedValue(taskFixtures[0]);
    apiMock.updateTask.mockResolvedValue(taskFixtures[0]);
    apiMock.deleteTask.mockResolvedValue({ status: "deleted" });
    apiMock.createDependency.mockResolvedValue(planFixture.dependencies[0]);
    apiMock.deleteDependency.mockResolvedValue({ status: "deleted" });
  });

  it("validates, approves, and edits DAG interactions through the API", async () => {
    renderRoute(<PlanEditorPage />, "/runs/:runId/plan", "/runs/run-1/plan?plan=plan-1");

    expect(await screen.findByText("DAG Editor")).toBeInTheDocument();
    expect(screen.getByText("DAG mock 2")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Validate DAG" }));
    await waitFor(() => expect(apiMock.validatePlan).toHaveBeenCalledWith("plan-1"));

    fireEvent.click(screen.getByRole("button", { name: "Approve Plan" }));
    await waitFor(() => expect(apiMock.approvePlan).toHaveBeenCalledWith("plan-1"));

    fireEvent.click(screen.getByRole("button", { name: "Connect Tasks" }));
    await waitFor(() => expect(apiMock.createDependency).toHaveBeenCalledWith("plan-1", { from_task_id: "task-1", to_task_id: "task-2" }));

    fireEvent.click(screen.getByRole("button", { name: "Move Task" }));
    await waitFor(() => expect(apiMock.updateTask).toHaveBeenCalledWith("task-1", { position_x: 10, position_y: 20 }));

    fireEvent.click(screen.getByRole("button", { name: /Remove dependency/ }));
    await waitFor(() => expect(apiMock.deleteDependency).toHaveBeenCalled());
    expect(apiMock.deleteDependency.mock.calls[0][0]).toBe("dep-1");
  });

  it("revises a locked plan into a new draft version", async () => {
    apiMock.listPlans.mockResolvedValue([{ ...planFixture, status: "LOCKED" }]);
    apiMock.getPlan.mockResolvedValue({ ...planFixture, status: "LOCKED" });

    renderRoute(<PlanEditorPage />, "/runs/:runId/plan", "/runs/run-1/plan?plan=plan-1");

    expect(await screen.findByText("DAG Editor")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Revise Plan" }));

    await waitFor(() => expect(apiMock.revisePlan).toHaveBeenCalledWith("plan-1"));
  });
});
