import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Boxes, GitBranch, Save } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { AutonomyLevel } from "../types/domain";

const defaults = {
  goal: "Build backend support for task DAG execution.",
  success_criteria: ["DAG can be created through API.", "Cycles are rejected.", "Approved plan can execute in dependency order.", "Dashboard can read execution status."],
  forbidden_losses: ["Do not delete existing tables.", "Do not run production commands."],
  allowed_tools: ["mock_executor", "command_executor", "test_runner"],
  human_approval_boundaries: ["before plan execution", "before irreversible operation"],
  risk_class: "MEDIUM",
  max_autonomy_level: "L3" as AutonomyLevel,
  notes: ""
};

export function ContractPage() {
  const { runId = "" } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const contract = useQuery({ queryKey: ["contract", runId], queryFn: () => api.getContract(runId), retry: false });
  const [draft, setDraft] = useState(defaults);

  useEffect(() => {
    if (contract.data) setDraft(contract.data);
  }, [contract.data]);

  const save = useMutation({
    mutationFn: () => api.saveContract(runId, draft),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["contract", runId] })
  });
  const generate = useMutation({
    mutationFn: () => api.generatePlan(runId),
    onSuccess: (plan) => {
      queryClient.invalidateQueries({ queryKey: ["plans", runId] });
      navigate(`/runs/${runId}/plan?plan=${plan.id}`);
    }
  });

  const setLines = (key: keyof typeof defaults, value: string) => setDraft({ ...draft, [key]: value.split("\n").map((line) => line.trim()).filter(Boolean) });

  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
      <section className="panel p-5">
        <div className="font-mono text-[11px] uppercase text-limewire">Task Contract</div>
        <h1 className="mt-2 font-display text-3xl font-black uppercase text-ink">Mission Boundary</h1>
        <label className="field-label mt-6">Mission Goal</label>
        <textarea className="loom-input min-h-28" value={draft.goal} onChange={(event) => setDraft({ ...draft, goal: event.target.value })} />
        <div className="grid gap-4 lg:grid-cols-2">
          <div>
            <label className="field-label">Success Criteria</label>
            <textarea className="loom-input min-h-36" value={draft.success_criteria.join("\n")} onChange={(event) => setLines("success_criteria", event.target.value)} />
          </div>
          <div>
            <label className="field-label">Forbidden Losses</label>
            <textarea className="loom-input min-h-36" value={draft.forbidden_losses.join("\n")} onChange={(event) => setLines("forbidden_losses", event.target.value)} />
          </div>
          <div>
            <label className="field-label">Allowed Tools</label>
            <textarea className="loom-input min-h-28" value={draft.allowed_tools.join("\n")} onChange={(event) => setLines("allowed_tools", event.target.value)} />
          </div>
          <div>
            <label className="field-label">Human Approval Boundaries</label>
            <textarea className="loom-input min-h-28" value={draft.human_approval_boundaries.join("\n")} onChange={(event) => setLines("human_approval_boundaries", event.target.value)} />
          </div>
        </div>
      </section>
      <aside className="space-y-4">
        <div className="panel p-5">
          <label className="field-label">Risk Class</label>
          <select className="loom-input" value={draft.risk_class} onChange={(event) => setDraft({ ...draft, risk_class: event.target.value })}>
            <option>LOW</option>
            <option>MEDIUM</option>
            <option>HIGH</option>
            <option>CRITICAL</option>
          </select>
          <label className="field-label">Max Autonomy</label>
          <select className="loom-input" value={draft.max_autonomy_level} onChange={(event) => setDraft({ ...draft, max_autonomy_level: event.target.value as AutonomyLevel })}>
            <option>L0</option>
            <option>L1</option>
            <option>L2</option>
            <option>L3</option>
            <option>L4</option>
            <option>L5</option>
          </select>
          <label className="field-label">Notes</label>
          <textarea className="loom-input min-h-24" value={draft.notes} onChange={(event) => setDraft({ ...draft, notes: event.target.value })} />
        </div>
        <div className="panel p-5">
          <button className="command-button w-full justify-center border-limewire/50 text-limewire" onClick={() => save.mutate()}>
            <Save size={16} /> Save Contract
          </button>
          <button className="command-button mt-3 w-full justify-center border-steel/40 text-ink" onClick={() => generate.mutate()}>
            <GitBranch size={16} /> Generate Plan
          </button>
          <div className="mt-5 flex items-center gap-3 border-t border-steel/10 pt-4 text-sm text-steel">
            <Boxes size={18} className="text-limewire" />
            Contract state persists in the backend and every save is ledgered.
          </div>
        </div>
      </aside>
    </div>
  );
}

