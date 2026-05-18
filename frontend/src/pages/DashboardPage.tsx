import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Pause, Play, RotateCw } from "lucide-react";
import { useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { api, streamUrl } from "../api/client";
import { EventTimeline } from "../components/EventTimeline";
import { StatusBadge } from "../components/StatusBadge";
import type { TaskNode } from "../types/domain";

export function DashboardPage() {
  const { runId = "" } = useParams();
  const queryClient = useQueryClient();
  const status = useQuery({ queryKey: ["status", runId], queryFn: () => api.getStatus(runId), refetchInterval: 5000 });
  const start = useMutation({ mutationFn: () => api.startRun(runId), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["status", runId] }) });
  const pause = useMutation({ mutationFn: () => api.pauseRun(runId), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["status", runId] }) });
  const resume = useMutation({ mutationFn: () => api.resumeRun(runId), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["status", runId] }) });

  useEffect(() => {
    if (!runId) return;
    const source = new EventSource(streamUrl(runId));
    source.onmessage = () => queryClient.invalidateQueries({ queryKey: ["status", runId] });
    source.addEventListener("TASK_STARTED", () => queryClient.invalidateQueries({ queryKey: ["status", runId] }));
    source.addEventListener("TASK_SUCCEEDED", () => queryClient.invalidateQueries({ queryKey: ["status", runId] }));
    source.addEventListener("TASK_REVIEW_REQUESTED", () => queryClient.invalidateQueries({ queryKey: ["status", runId] }));
    source.addEventListener("RUN_COMPLETED", () => queryClient.invalidateQueries({ queryKey: ["status", runId] }));
    return () => source.close();
  }, [queryClient, runId]);

  const snapshot = status.data;
  const tasks = snapshot?.plan?.tasks ?? [];
  const running = tasks.filter((task) => ["QUEUED", "RUNNING", "VERIFYING"].includes(task.status));
  const blocked = tasks.filter((task) => task.status === "BLOCKED");
  const failed = tasks.filter((task) => task.status === "FAILED");
  const review = tasks.filter((task) => ["AWAITING_REVIEW", "NEEDS_HUMAN"].includes(task.status));

  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
      <section className="space-y-5">
        <div className="panel p-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="font-mono text-[11px] uppercase text-limewire">Execution Dashboard</div>
              <h1 className="mt-2 font-display text-3xl font-black uppercase text-ink">{snapshot?.run.name ?? "Run"}</h1>
              <p className="mt-2 text-sm text-steel">{snapshot?.run.description}</p>
            </div>
            {snapshot?.run.status && <StatusBadge status={snapshot.run.status} />}
          </div>
          <div className="mt-5 flex flex-wrap gap-2">
            <button className="command-button border-limewire/50 text-limewire" onClick={() => start.mutate()}>
              <Play size={15} /> Start
            </button>
            <button className="command-button border-steel/40 text-steel" onClick={() => pause.mutate()}>
              <Pause size={15} /> Pause
            </button>
            <button className="command-button border-steel/40 text-steel" onClick={() => resume.mutate()}>
              <RotateCw size={15} /> Resume
            </button>
            <Link className="command-button border-amber-300/50 text-amber-200" to={`/runs/${runId}/reviews`}>
              <Activity size={15} /> Review Queue
            </Link>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Counter label="Running" value={running.length} />
          <Counter label="Blocked" value={blocked.length} />
          <Counter label="Failed" value={failed.length} />
          <Counter label="Needs Human" value={review.length} />
        </div>

        <TaskLane title="Current Running Tasks" tasks={running} />
        <TaskLane title="Blocked Tasks" tasks={blocked} />
        <TaskLane title="Failed Tasks" tasks={failed} />
        <TaskLane title="Tasks Needing Human Review" tasks={review} />
      </section>

      <aside className="space-y-5">
        <section className="panel p-4">
          <div className="mb-4 font-mono text-[11px] uppercase text-limewire">Verifier Results</div>
          <div className="space-y-3">
            {snapshot?.verification_results.slice(0, 8).map((result) => (
              <div key={result.id} className="border border-steel/20 p-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="font-mono text-[11px] uppercase text-ink">{result.verifier_name}</div>
                  <StatusBadge status={result.status} />
                </div>
                <p className="mt-2 text-xs text-steel">{result.summary}</p>
              </div>
            ))}
            {!snapshot?.verification_results.length && <div className="text-sm text-steel">No verifier results yet.</div>}
          </div>
        </section>
        <section className="panel p-4">
          <div className="mb-4 font-mono text-[11px] uppercase text-limewire">State Ledger</div>
          <EventTimeline events={snapshot?.events ?? []} />
        </section>
      </aside>
    </div>
  );
}

function Counter({ label, value }: { label: string; value: number }) {
  return (
    <div className="panel p-4">
      <div className="font-mono text-[10px] uppercase text-steel">{label}</div>
      <div className="font-display text-4xl font-black text-ink">{value}</div>
    </div>
  );
}

function TaskLane({ title, tasks }: { title: string; tasks: TaskNode[] }) {
  return (
    <section className="panel p-4">
      <div className="mb-3 font-mono text-[11px] uppercase text-limewire">{title}</div>
      <div className="grid gap-3 md:grid-cols-2">
        {tasks.map((task) => (
          <article key={task.id} className="border border-steel/20 p-3">
            <div className="flex items-start justify-between gap-3">
              <h3 className="font-display text-base font-semibold text-ink">{task.title}</h3>
              <StatusBadge status={task.status} />
            </div>
            <p className="mt-2 line-clamp-2 text-xs text-steel">{task.description}</p>
          </article>
        ))}
      </div>
      {!tasks.length && <div className="text-sm text-steel">None.</div>}
    </section>
  );
}

