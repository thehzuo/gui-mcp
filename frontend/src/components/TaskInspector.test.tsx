import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { taskFixtures } from "../test/fixtures";
import { renderWithApp } from "../test/test-utils";
import { TaskInspector } from "./TaskInspector";

describe("TaskInspector", () => {
  it("edits a selected task and emits a scoped update payload", () => {
    const onSave = vi.fn();
    const onDelete = vi.fn();

    renderWithApp(<TaskInspector task={taskFixtures[0]} locked={false} onSave={onSave} onDelete={onDelete} />);

    const titleInput = screen.getByDisplayValue("Inspect current mission boundary");
    fireEvent.change(titleInput, { target: { value: "Inspect durable kernel" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(onSave).toHaveBeenCalledWith("task-1", expect.objectContaining({ title: "Inspect durable kernel" }));
  });

  it("disables structural actions for locked plans", () => {
    renderWithApp(<TaskInspector task={taskFixtures[0]} locked={true} onSave={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Delete" })).toBeDisabled();
  });
});

