import { Save, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import type { TaskNode } from "../types/domain";
import { StatusBadge } from "./StatusBadge";

interface TaskInspectorProps {
  task: TaskNode | null;
  locked: boolean;
  onSave: (taskId: string, payload: Partial<TaskNode>) => void;
  onDelete: (taskId: string) => void;
}

export function TaskInspector({ task, locked, onSave, onDelete }: TaskInspectorProps) {
  const [draft, setDraft] = useState<TaskNode | null>(task);
  const [configText, setConfigText] = useState("");
  const [configError, setConfigError] = useState("");

  useEffect(() => {
    setDraft(task);
    setConfigText(JSON.stringify(task?.executor_config_json ?? {}, null, 2));
    setConfigError("");
  }, [task]);

  if (!draft || !task) {
    return <div className="panel p-4 text-sm text-steel">Select a task node to inspect its contract, risk, verifier, and executor boundary.</div>;
  }

  const update = <K extends keyof TaskNode>(key: K, value: TaskNode[K]) => setDraft({ ...draft, [key]: value });
  const arrayValue = (value: string) => value.split("\n").map((item) => item.trim()).filter(Boolean);
  const updateConfig = (key: string, value: unknown) => {
    const next = { ...draft.executor_config_json, [key]: value };
    update("executor_config_json", next);
    setConfigText(JSON.stringify(next, null, 2));
    setConfigError("");
  };
  const parseConfig = (value: string) => {
    setConfigText(value);
    try {
      const parsed = JSON.parse(value || "{}") as Record<string, unknown>;
      update("executor_config_json", parsed);
      setConfigError("");
    } catch {
      setConfigError("Executor config must be valid JSON.");
    }
  };
  const savePayload = (): Partial<TaskNode> => ({
    title: draft.title,
    description: draft.description,
    task_family: draft.task_family,
    risk_level: draft.risk_level,
    reversibility: draft.reversibility,
    required_autonomy_level: draft.required_autonomy_level,
    assigned_model_id: draft.assigned_model_id,
    expected_outputs: draft.expected_outputs,
    verifier_refs: draft.verifier_refs,
    tool_refs: draft.tool_refs,
    executor_type: draft.executor_type,
    executor_config_json: draft.executor_config_json,
    human_review_required: draft.human_review_required,
    position_x: draft.position_x,
    position_y: draft.position_y
  });

  return (
    <aside className="panel h-full overflow-auto p-4">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <div className="font-mono text-[10px] uppercase text-steel">Task Inspector</div>
          <h2 className="mt-1 font-display text-xl font-semibold text-ink">{draft.title}</h2>
        </div>
        <StatusBadge status={draft.status} />
      </div>
      <label className="field-label">Title</label>
      <input className="loom-input" value={draft.title} disabled={locked} onChange={(event) => update("title", event.target.value)} />
      <label className="field-label">Description</label>
      <textarea className="loom-input min-h-24" value={draft.description} disabled={locked} onChange={(event) => update("description", event.target.value)} />
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="field-label">Task Family</label>
          <input className="loom-input" value={draft.task_family} disabled={locked} onChange={(event) => update("task_family", event.target.value)} />
        </div>
        <div>
          <label className="field-label">Model</label>
          <input className="loom-input" value={draft.assigned_model_id} disabled={locked} onChange={(event) => update("assigned_model_id", event.target.value)} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="field-label">Risk</label>
          <select className="loom-input" value={draft.risk_level} disabled={locked} onChange={(event) => update("risk_level", event.target.value as TaskNode["risk_level"])}>
            <option>LOW</option>
            <option>MEDIUM</option>
            <option>HIGH</option>
            <option>CRITICAL</option>
          </select>
        </div>
        <div>
          <label className="field-label">Autonomy</label>
          <select className="loom-input" value={draft.required_autonomy_level} disabled={locked} onChange={(event) => update("required_autonomy_level", event.target.value as TaskNode["required_autonomy_level"])}>
            <option>L0</option>
            <option>L1</option>
            <option>L2</option>
            <option>L3</option>
            <option>L4</option>
            <option>L5</option>
          </select>
        </div>
      </div>
      <label className="field-label">Reversibility</label>
      <select className="loom-input" value={draft.reversibility} disabled={locked} onChange={(event) => update("reversibility", event.target.value as TaskNode["reversibility"])}>
        <option>REVERSIBLE</option>
        <option>PARTIALLY_REVERSIBLE</option>
        <option>IRREVERSIBLE</option>
      </select>
      <label className="field-label">Expected Outputs</label>
      <textarea className="loom-input min-h-20" value={draft.expected_outputs.join("\n")} disabled={locked} onChange={(event) => update("expected_outputs", arrayValue(event.target.value))} />
      <label className="field-label">Verifier Refs</label>
      <textarea className="loom-input min-h-16" value={draft.verifier_refs.join("\n")} disabled={locked} onChange={(event) => update("verifier_refs", arrayValue(event.target.value))} />
      <label className="field-label">Tool Refs</label>
      <textarea className="loom-input min-h-16" value={draft.tool_refs.join("\n")} disabled={locked} onChange={(event) => update("tool_refs", arrayValue(event.target.value))} />
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="field-label">Executor</label>
          <select className="loom-input" value={draft.executor_type} disabled={locked} onChange={(event) => update("executor_type", event.target.value as TaskNode["executor_type"])}>
            <option value="mock">mock</option>
            <option value="command">command</option>
          </select>
        </div>
        <div>
          <label className="field-label">Review Status</label>
          <select className="loom-input" value={draft.review_status} disabled={locked} onChange={(event) => update("review_status", event.target.value as TaskNode["review_status"])}>
            <option>NOT_REQUIRED</option>
            <option>PENDING</option>
            <option>APPROVED</option>
            <option>REJECTED</option>
          </select>
        </div>
      </div>
      {draft.executor_type === "command" ? (
        <>
          <label className="field-label">Command</label>
          <input aria-label="Command" className="loom-input" value={String(draft.executor_config_json.command ?? "")} disabled={locked} onChange={(event) => updateConfig("command", event.target.value)} />
          <label className="field-label">Working Directory</label>
          <input aria-label="Working Directory" className="loom-input" value={String(draft.executor_config_json.cwd ?? "")} disabled={locked} onChange={(event) => updateConfig("cwd", event.target.value)} />
        </>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="field-label">Mock Delay</label>
            <input className="loom-input" type="number" min="0" step="0.05" value={Number(draft.executor_config_json.delay_seconds ?? 0.25)} disabled={locked} onChange={(event) => updateConfig("delay_seconds", Number(event.target.value))} />
          </div>
          <label className="mt-9 flex min-h-[44px] items-center gap-2 border border-steel/20 bg-carbon/50 px-3 text-sm text-ink">
            <input type="checkbox" checked={Boolean(draft.executor_config_json.should_fail)} disabled={locked} onChange={(event) => updateConfig("should_fail", event.target.checked)} />
            Mock failure
          </label>
        </div>
      )}
      <label className="field-label">Executor Config JSON</label>
      <textarea className="loom-input min-h-28 font-mono text-xs" value={configText} disabled={locked} onChange={(event) => parseConfig(event.target.value)} />
      {configError && <div className="mt-2 text-xs text-ember">{configError}</div>}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="field-label">Position X</label>
          <input className="loom-input" type="number" value={draft.position_x} disabled={locked} onChange={(event) => update("position_x", Number(event.target.value))} />
        </div>
        <div>
          <label className="field-label">Position Y</label>
          <input className="loom-input" type="number" value={draft.position_y} disabled={locked} onChange={(event) => update("position_y", Number(event.target.value))} />
        </div>
      </div>
      <label className="mt-3 flex items-center gap-2 text-sm text-ink">
        <input type="checkbox" checked={draft.human_review_required} disabled={locked} onChange={(event) => update("human_review_required", event.target.checked)} />
        Requires human review
      </label>
      <div className="mt-4 flex flex-wrap gap-2">
        <button className="command-button border-limewire/50 text-limewire" disabled={locked || Boolean(configError)} onClick={() => onSave(task.id, savePayload())}>
          <Save size={15} /> Save
        </button>
        <button className="command-button border-ember/50 text-ember" disabled={locked} onClick={() => onDelete(task.id)}>
          <Trash2 size={15} /> Delete
        </button>
      </div>
    </aside>
  );
}
