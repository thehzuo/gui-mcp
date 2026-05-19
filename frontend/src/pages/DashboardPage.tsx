import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Pause, Play, RotateCw, TerminalSquare } from "lucide-react";
import { useEffect, useMemo, useRef } from "react";
import { Link, useParams } from "react-router-dom";
import { api, streamUrl } from "../api/client";
import { EventTimeline } from "../components/EventTimeline";
import { StatusBadge } from "../components/StatusBadge";
import type { PolicySummary, ReviewRecord, TaskExecution, TaskNode } from "../types/domain";

export function DashboardPage() {
  const { runId = "" } = useParams();
  const queryClient = useQueryClient();
  const status = useQuery({ queryKey: ["status", runId], queryFn: () => api.getStatus(runId), refetchInterval: 5000 });
  const start = useMutation({ mutationFn: () => api.startRun(runId), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["status", runId] }) });
  const pause = useMutation({ mutationFn: () => api.pauseRun(runId), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["status", runId] }) });
  const resume = useMutation({ mutationFn: () => api.resumeRun(runId), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["status", runId] }) });
  const lastEventId = useRef<string | null>(null);

  useEffect(() => {
    if (!runId) return;
    const source = new EventSource(streamUrl(runId));
    const resync = (event?: MessageEvent) => {
      if (event?.lastEventId) lastEventId.current = event.lastEventId;
      if (lastEventId.current) api.getEvents(runId, lastEventId.current).catch(() => undefined);
      queryClient.invalidateQueries({ queryKey: ["status", runId] });
    };
    source.onopen = () => resync();
    source.onerror = () => resync();
    source.onmessage = resync;
    ["TASK_STARTED", "TASK_OUTPUT_RECORDED", "TASK_SUCCEEDED", "TASK_FAILED", "TASK_BLOCKED", "TASK_REVIEW_REQUESTED", "RUN_COMPLETED"].forEach((eventName) => {
      source.addEventListener(eventName, resync);
    });
    return () => source.close();
  }, [queryClient, runId]);

  const snapshot = status.data;
  const tasks = snapshot?.plan?.tasks ?? [];
  const executionsByTask = useMemo(() => {
    const grouped: Record<string, TaskExecution[]> = {};
    for (const execution of snapshot?.task_executions ?? []) {
      grouped[execution.task_id] = [...(grouped[execution.task_id] ?? []), execution];
    }
    return grouped;
  }, [snapshot?.task_executions]);
  const running = tasks.filter((task) => ["QUEUED", "RUNNING", "VERIFYING"].includes(task.status));
  const blocked = tasks.filter((task) => task.status === "BLOCKED");
  const failed = tasks.filter((task) => task.status === "FAILED");
  const review = tasks.filter((task) => ["AWAITING_REVIEW", "NEEDS_HUMAN"].includes(task.status));
  const pendingReviews = snapshot?.reviews.filter((item) => item.status === "PENDING") ?? [];

  return (
    <div className="grid min-w-0 gap-5 xl:grid-cols-[1fr_360px]">
      <section className="min-w-0 space-y-5">
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

        <TaskLane title="Current Running Tasks" tasks={running} executionsByTask={executionsByTask} policy={snapshot?.policy_summaries ?? {}} reasons={{}} />
        <TaskLane title="Blocked Tasks" tasks={blocked} executionsByTask={executionsByTask} policy={snapshot?.policy_summaries ?? {}} reasons={snapshot?.blocked_reasons ?? {}} />
        <TaskLane title="Failed Tasks" tasks={failed} executionsByTask={executionsByTask} policy={snapshot?.policy_summaries ?? {}} reasons={snapshot?.blocked_reasons ?? {}} />
        <TaskLane title="Tasks Needing Human Review" tasks={review} executionsByTask={executionsByTask} policy={snapshot?.policy_summaries ?? {}} reasons={snapshot?.review_reasons ?? {}} />
        <ExecutionHistory tasks={tasks} executions={snapshot?.task_executions ?? []} />
      </section>

      <aside className="min-w-0 space-y-5">
        <section className="panel p-4">
          <div className="mb-4 font-mono text-[11px] uppercase text-limewire">Pending Reviews</div>
          <div className="space-y-3">
            {pendingReviews.slice(0, 5).map((review) => (
              <ReviewSummary key={review.id} review={review} task={tasks.find((task) => task.id === review.task_id)} />
            ))}
            {!pendingReviews.length && <div className="text-sm text-steel">No pending review packets.</div>}
          </div>
        </section>
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

function TaskLane({
  title,
  tasks,
  reasons,
  policy,
  executionsByTask
}: {
  title: string;
  tasks: TaskNode[];
  reasons: Record<string, string>;
  policy: Record<string, PolicySummary>;
  executionsByTask: Record<string, TaskExecution[]>;
}) {
  return (
    <section className="panel p-4">
      <div className="mb-3 font-mono text-[11px] uppercase text-limewire">{title}</div>
      <div className="grid gap-3 md:grid-cols-2">
        {tasks.map((task) => {
          const latestExecution = executionsByTask[task.id]?.[0];
          const policySummary = policy[task.id];
          return (
            <article key={task.id} className="border border-steel/20 p-3">
              <div className="flex items-start justify-between gap-3">
                <h3 className="font-display text-base font-semibold text-ink">{task.title}</h3>
                <StatusBadge status={task.status} />
              </div>
              <p className="mt-2 line-clamp-2 text-xs text-steel">{task.description}</p>
              {reasons[task.id] && <div className="mt-3 border-l-2 border-amber-300/70 pl-3 text-xs text-amber-100">{reasons[task.id]}</div>}
              {policySummary && (
                <div className="mt-3 grid gap-1 border border-steel/15 bg-carbon/40 p-2 font-mono text-[10px] uppercase text-steel">
                  <span className="text-ink">{policySummary.decision}</span>
                  <span>{policySummary.reason}</span>
                  <span>{policySummary.required_action}</span>
                </div>
              )}
              {latestExecution && (
                <div className="mt-3 flex flex-wrap gap-2 font-mono text-[10px] uppercase text-steel">
                  <span>exit {latestExecution.exit_code ?? "n/a"}</span>
                  <span>{latestExecution.duration_ms}ms</span>
                  <span>{latestExecution.executor_type}</span>
                </div>
              )}
            </article>
          );
        })}
      </div>
      {!tasks.length && <div className="text-sm text-steel">None.</div>}
    </section>
  );
}

function ExecutionHistory({ tasks, executions }: { tasks: TaskNode[]; executions: TaskExecution[] }) {
  const taskTitle = (taskId: string) => tasks.find((task) => task.id === taskId)?.title ?? taskId.slice(0, 8);
  return (
    <section className="panel p-4">
      <div className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase text-limewire">
        <TerminalSquare size={15} /> Artifacts / Outputs
      </div>
      <div className="space-y-3">
        {executions.slice(0, 8).map((execution) => (
          <article key={execution.id} className="border border-steel/20 bg-carbon/40 p-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="font-display text-base font-semibold text-ink">{taskTitle(execution.task_id)}</h3>
              <div className="flex flex-wrap gap-2 font-mono text-[10px] uppercase text-steel">
                <span>{execution.executor_type}</span>
                <span>exit {execution.exit_code ?? "n/a"}</span>
                <span>{execution.duration_ms}ms</span>
              </div>
            </div>
            {execution.command && <pre className="mt-2 overflow-auto border border-steel/15 bg-black/25 p-2 text-xs text-ink">{execution.command}</pre>}
            {execution.stdout && <pre className="mt-2 max-h-32 overflow-auto whitespace-pre-wrap border border-limewire/20 bg-black/25 p-2 text-xs text-ink">{execution.stdout}</pre>}
            {execution.stderr && <pre className="mt-2 max-h-32 overflow-auto whitespace-pre-wrap border border-ember/30 bg-black/25 p-2 text-xs text-ember">{execution.stderr}</pre>}
          </article>
        ))}
        {!executions.length && <div className="text-sm text-steel">No task outputs recorded yet.</div>}
      </div>
    </section>
  );
}

function ReviewSummary({ review, task }: { review: ReviewRecord; task?: TaskNode }) {
  return (
    <div className="border border-steel/20 p-3">
      <div className="flex items-center justify-between gap-2">
        <div className="font-mono text-[11px] uppercase text-ink">{review.review_type}</div>
        <StatusBadge status={review.status} />
      </div>
      <p className="mt-2 text-sm text-ink">{task?.title ?? String(review.packet_json.plan_summary ?? "Plan review")}</p>
      <p className="mt-1 text-xs text-steel">{review.reason}</p>
    </div>
  );
}
