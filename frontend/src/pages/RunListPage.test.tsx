import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { runFixture } from "../test/fixtures";
import { renderWithApp } from "../test/test-utils";
import { RunListPage } from "./RunListPage";

const apiMock = vi.hoisted(() => ({
  listRuns: vi.fn(),
  createRun: vi.fn(),
  cancelRun: vi.fn()
}));

vi.mock("../api/client", () => ({ api: apiMock }));

describe("RunListPage", () => {
  beforeEach(() => {
    apiMock.listRuns.mockResolvedValue([runFixture]);
    apiMock.createRun.mockResolvedValue(runFixture);
    apiMock.cancelRun.mockResolvedValue({ ...runFixture, status: "CANCELED" });
  });

  it("loads runs and creates a new run from mission intake", async () => {
    renderWithApp(<RunListPage />);

    expect(await screen.findByText("Build DAG execution backend")).toBeInTheDocument();
    expect(screen.getByText(/SUCCEEDED:2\s+AWAITING_REVIEW:1/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Create Run" }));

    await waitFor(() => expect(apiMock.createRun).toHaveBeenCalled());
    expect(apiMock.createRun.mock.calls[0][0]).toEqual(expect.objectContaining({ name: "Build DAG execution backend" }));
  });
});
