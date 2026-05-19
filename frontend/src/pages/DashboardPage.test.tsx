import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { runFixture, statusFixture } from "../test/fixtures";
import { renderRoute } from "../test/test-utils";
import { DashboardPage } from "./DashboardPage";

const apiMock = vi.hoisted(() => ({
  getStatus: vi.fn(),
  startRun: vi.fn(),
  pauseRun: vi.fn(),
  resumeRun: vi.fn(),
  getEvents: vi.fn()
}));

vi.mock("../api/client", () => ({
  api: apiMock,
  streamUrl: (runId: string) => `/api/runs/${runId}/stream`
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    apiMock.getStatus.mockResolvedValue(statusFixture);
    apiMock.startRun.mockResolvedValue({ status: "started", run_id: "run-1" });
    apiMock.pauseRun.mockResolvedValue({ ...runFixture, status: "PAUSED" });
    apiMock.resumeRun.mockResolvedValue(runFixture);
    apiMock.getEvents.mockResolvedValue([]);
  });

  it("renders run health, verifier results, ledger events, and starts execution", async () => {
    renderRoute(<DashboardPage />, "/runs/:runId/dashboard", "/runs/run-1/dashboard");

    expect(await screen.findByText("Build DAG execution backend")).toBeInTheDocument();
    expect(screen.getByText("Verifier Results")).toBeInTheDocument();
    expect(screen.getByText("Artifacts / Outputs")).toBeInTheDocument();
    expect(screen.getByText("TASK_REVIEW_REQUESTED")).toBeInTheDocument();
    expect(screen.getAllByText("Review risky boundary").length).toBeGreaterThan(0);
    expect(screen.getByText("loom")).toBeInTheDocument();
    expect(screen.getByText("HUMAN_REVIEW_REQUIRED")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Start" }));
    await waitFor(() => expect(apiMock.startRun).toHaveBeenCalledWith("run-1"));
  });
});
