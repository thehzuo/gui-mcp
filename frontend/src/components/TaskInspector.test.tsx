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
    fireEvent.change(screen.getByDisplayValue("code_analysis"), { target: { value: "coding_change" } });
    fireEvent.change(screen.getByDisplayValue("local-default"), { target: { value: "local-default" } });
    fireEvent.change(screen.getByDisplayValue("command_exit_code"), { target: { value: "command_exit_code\nmanual_verifier" } });
    fireEvent.change(screen.getByDisplayValue("mock_executor"), { target: { value: "command_executor" } });
    fireEvent.change(screen.getByDisplayValue("mock"), { target: { value: "command" } });
    fireEvent.change(screen.getByLabelText("Command"), { target: { value: "printf loom" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));

    expect(onSave).toHaveBeenCalledWith(
      "task-1",
      expect.objectContaining({
        title: "Inspect durable kernel",
        task_family: "coding_change",
        verifier_refs: ["command_exit_code", "manual_verifier"],
        tool_refs: ["command_executor"],
        executor_type: "command",
        executor_config_json: expect.objectContaining({ command: "printf loom" })
      })
    );
  });

  it("disables structural actions for locked plans", () => {
    renderWithApp(<TaskInspector task={taskFixtures[0]} locked={true} onSave={vi.fn()} onDelete={vi.fn()} />);

    expect(screen.getByRole("button", { name: "Save" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Delete" })).toBeDisabled();
  });
});
