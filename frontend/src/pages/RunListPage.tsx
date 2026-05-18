import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, CircleStop, Plus } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";

export function RunListPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [name, setName] = useState("Build DAG execution backend");
  const [description, setDescription] = useState("Implement a reviewed task DAG and execution dashboard.");
  const runs = useQuery({ queryKey: ["runs"], queryFn: api.listRuns });
  const createRun = useMutation({
    mutationFn: api.createRun,
    onSuccess: (run) => {
      queryClient.invalidateQueries({ queryKey: ["runs"] });
      navigate(`/runs/${run.id}/contract`);
    }
  });
  const cancelRun = useMutation({
    mutationFn: api.cancelRun,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["runs"] })
  });

  return (
    <div className="grid min-h-[calc(100vh-80px)] gap-5 xl:grid-cols-[420px_1fr]">
      <section className="panel p-5">
        <div className="font-mono text-[11px] uppercase text-limewire">Mission Intake</div>
        <h1 className="mt-2 font-display text-3xl font-black uppercase leading-none text-ink">Agent Loom</h1>
        <p className="mt-3 text-sm leading-6 text-steel">Create a mission, compile it into a Task Contract, review the DAG, then execute with ledgered control gates.</p>
        <label className="field-label mt-6">Run Name</label>
        <input className="loom-input" value={name} onChange={(event) => setName(event.target.value)} />
        <label className="field-label">Description</label>
        <textarea className="loom-input min-h-28" value={description} onChange={(event) => setDescription(event.target.value)} />
        <button className="command-button mt-5 border-limewire/50 text-limewire" onClick={() => createRun.mutate({ name, description })}>
          <Plus size={16} /> Create Run
        </button>
      </section>

      <section className="panel overflow-hidden">
        <div className="grid grid-cols-[1.5fr_140px_160px_120px] border-b border-steel/20 px-4 py-3 font-mono text-[11px] uppercase text-steel">
          <span>Run</span>
          <span>Status</span>
          <span>Progress</span>
          <span>Action</span>
        </div>
        <div className="divide-y divide-steel/10">
          {runs.data?.map((run) => (
            <div key={run.id} className="grid grid-cols-[1.5fr_140px_160px_120px] items-center gap-3 px-4 py-4">
              <div>
                <div className="font-display text-lg font-semibold text-ink">{run.name}</div>
                <div className="mt-1 line-clamp-1 text-sm text-steel">{run.description}</div>
              </div>
              <StatusBadge status={run.status} />
              <div className="font-mono text-xs text-steel">
                {Object.entries(run.progress_summary).map(([status, count]) => `${status}:${count}`).join("  ") || "no tasks"}
              </div>
              <div className="flex gap-2">
                <Link className="icon-button" to={`/runs/${run.id}/dashboard`} title="Open run">
                  <ArrowRight size={16} />
                </Link>
                <button className="icon-button text-ember" onClick={() => cancelRun.mutate(run.id)} title="Cancel run">
                  <CircleStop size={16} />
                </button>
              </div>
            </div>
          ))}
          {!runs.data?.length && <div className="px-4 py-8 text-sm text-steel">No runs yet.</div>}
        </div>
      </section>
    </div>
  );
}

