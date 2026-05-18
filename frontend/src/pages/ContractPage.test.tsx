import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { contractFixture, planFixture } from "../test/fixtures";
import { renderRoute } from "../test/test-utils";
import { ContractPage } from "./ContractPage";

const apiMock = vi.hoisted(() => ({
  getContract: vi.fn(),
  saveContract: vi.fn(),
  generatePlan: vi.fn()
}));

vi.mock("../api/client", () => ({ api: apiMock }));

describe("ContractPage", () => {
  beforeEach(() => {
    apiMock.getContract.mockResolvedValue(contractFixture);
    apiMock.saveContract.mockResolvedValue(contractFixture);
    apiMock.generatePlan.mockResolvedValue(planFixture);
  });

  it("renders the task contract and calls save/generate APIs", async () => {
    renderRoute(<ContractPage />, "/runs/:runId/contract", "/runs/run-1/contract");

    expect(await screen.findByDisplayValue("Build backend support for task DAG execution.")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Save Contract" }));
    await waitFor(() => expect(apiMock.saveContract).toHaveBeenCalledWith("run-1", expect.objectContaining({ max_autonomy_level: "L3" })));

    fireEvent.click(screen.getByRole("button", { name: "Generate Plan" }));
    await waitFor(() => expect(apiMock.generatePlan).toHaveBeenCalledWith("run-1"));
  });
});

