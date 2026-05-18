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

  useEffect(() => {
    setDraft(task);
  }, [task]);

  if (!draft || !task) {
    return <div className="panel p-4 text-sm text-steel">Select a task node to inspect its contract, risk, verifier, and executor boundary.</div>;
  }

  const update = <K extends keyof TaskNode>(key: K, value: TaskNode[K]) => setDraft({ ...draft, [key]: value });
  const arrayValue = (value: string) => value.split("\n").map((item) => item.trim()).filter(Boolean);

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
      <input className="loom-input" value={draft.verifier_refs.join(", ")} disabled={locked} onChange={(event) => update("verifier_refs", event.target.value.split(",").map((item) => item.trim()).filter(Boolean))} />
      <label className="field-label">Executor</label>
      <select className="loom-input" value={draft.executor_type} disabled={locked} onChange={(event) => update("executor_type", event.target.value as TaskNode["executor_type"])}>
        <option value="mock">mock</option>
        <option value="command">command</option>
      </select>
      <label className="mt-3 flex items-center gap-2 text-sm text-ink">
        <input type="checkbox" checked={draft.human_review_required} disabled={locked} onChange={(event) => update("human_review_required", event.target.checked)} />
        Requires human review
      </label>
      <div className="mt-4 flex flex-wrap gap-2">
        <button className="command-button border-limewire/50 text-limewire" disabled={locked} onClick={() => onSave(task.id, draft)}>
          <Save size={15} /> Save
        </button>
        <button className="command-button border-ember/50 text-ember" disabled={locked} onClick={() => onDelete(task.id)}>
          <Trash2 size={15} /> Delete
        </button>
      </div>
    </aside>
  );
}

