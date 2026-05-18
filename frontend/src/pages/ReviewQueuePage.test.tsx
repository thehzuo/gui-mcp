import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { reviewFixture } from "../test/fixtures";
import { renderRoute } from "../test/test-utils";
import { ReviewQueuePage } from "./ReviewQueuePage";

const apiMock = vi.hoisted(() => ({
  listReviews: vi.fn(),
  approveReview: vi.fn(),
  rejectReview: vi.fn(),
  requestChanges: vi.fn()
}));

vi.mock("../api/client", () => ({ api: apiMock }));

describe("ReviewQueuePage", () => {
  beforeEach(() => {
    apiMock.listReviews.mockResolvedValue([reviewFixture]);
    apiMock.approveReview.mockResolvedValue({ ...reviewFixture, status: "APPROVED" });
    apiMock.rejectReview.mockResolvedValue({ ...reviewFixture, status: "REJECTED" });
    apiMock.requestChanges.mockResolvedValue({ ...reviewFixture, status: "CHANGES_REQUESTED" });
  });

  it("renders pending review packets and approves one", async () => {
    renderRoute(<ReviewQueuePage />, "/runs/:runId/reviews", "/runs/run-1/reviews");

    expect(await screen.findByText("Review risky boundary")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Approve" }));

    await waitFor(() => expect(apiMock.approveReview).toHaveBeenCalledWith("review-1"));
  });
});

