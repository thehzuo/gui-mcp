import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReviewPacket } from "./ReviewPacket";
import { reviewFixture } from "../test/fixtures";
import { renderWithApp } from "../test/test-utils";

describe("ReviewPacket", () => {
  it("renders compact decision packet and wires review actions", () => {
    const onApprove = vi.fn();
    const onReject = vi.fn();
    const onChanges = vi.fn();

    renderWithApp(<ReviewPacket review={reviewFixture} onApprove={onApprove} onReject={onReject} onChanges={onChanges} />);

    expect(screen.getByText("Review risky boundary")).toBeInTheDocument();
    expect(screen.getByText("Task is high risk and verifier strength is NONE.")).toBeInTheDocument();
    expect(screen.getByText("HIGH")).toBeInTheDocument();
    expect(screen.getByText("NONE")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Approve" }));
    fireEvent.click(screen.getByRole("button", { name: "Changes" }));
    fireEvent.click(screen.getByRole("button", { name: "Reject" }));

    expect(onApprove).toHaveBeenCalledOnce();
    expect(onChanges).toHaveBeenCalledOnce();
    expect(onReject).toHaveBeenCalledOnce();
  });
});

