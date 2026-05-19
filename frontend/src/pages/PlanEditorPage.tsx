import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CheckCircle2, GitPullRequest, Plus, RefreshCw, ShieldCheck, Trash2, XCircle } from "lucide-react";
import { useMemo, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { DagCanvas } from "../components/DagCanvas";
import { StatusBadge } from "../components/StatusBadge";
import { TaskInspector } from "../components/TaskInspector";
import type { TaskNode, ValidationResult } from "../types/domain";

export function PlanEditorPage() {
  const { runId = "" } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const plans = useQuery({ queryKey: ["plans", runId], queryFn: () => api.listPlans(runId) });
  const activePlanId = searchParams.get("plan") ?? plans.data?.[plans.data.length - 1]?.id;
  const plan = useQuery({ queryKey: ["plan", activePlanId], queryFn: () => api.getPlan(activePlanId!), enabled: Boolean(activePlanId) });
  const [selectedTask, setSelectedTask] = useState<TaskNode | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const editable = plan.data?.status === "DRAFT" || plan.data?.status === "AWAITING_REVIEW";
  const locked = !editable;

  const invalidatePlan = () => {
    queryClient.invalidateQueries({ queryKey: ["plans", runId] });
    queryClient.invalidateQueries({ queryKey: ["plan", activePlanId] });
  };
  const refreshPlanAndValidation = async () => {
    invalidatePlan();
    if (activePlanId) {
      try {
        setValidation(await api.validatePlan(activePlanId));
      } catch {
        setValidation(null);
      }
    }
  };

  const validate = useMutation({ mutationFn: () => api.validatePlan(activePlanId!), onSuccess: (result) => { setValidation(result); invalidatePlan(); } });
  const submit = useMutation({ mutationFn: () => api.submitPlanReview(activePlanId!), onSuccess: invalidatePlan });
  const approve = useMutation({ mutationFn: () => api.approvePlan(activePlanId!), onSuccess: invalidatePlan });
  const reject = useMutation({ mutationFn: () => api.rejectPlan(activePlanId!), onSuccess: invalidatePlan });
  const revise = useMutation({
    mutationFn: () => api.revisePlan(activePlanId!),
    onSuccess: (revised) => {
      setValidation(null);
      queryClient.invalidateQueries({ queryKey: ["plans", runId] });
      setSearchParams({ plan: revised.id });
    }
  });
  const createTask = useMutation({
    mutationFn: () =>
      api.createTask(activePlanId!, {
        title: "New task",
        description: "Describe the task boundary and expected action.",
        task_family: "general",
        risk_level: "LOW",
        reversibility: "REVERSIBLE",
        required_autonomy_level: "L3",
        expected_outputs: ["Task output"],
        verifier_refs: ["command_exit_code"],
        tool_refs: ["mock_executor"],
        executor_type: "mock",
        executor_config_json: { delay_seconds: 0.25, should_fail: false },
        position_x: 120,
        position_y: 120
      }),
    onSuccess: refreshPlanAndValidation
  });
  const updateTask = useMutation({
    mutationFn: ({ taskId, payload }: { taskId: string; payload: Partial<TaskNode> }) => api.updateTask(taskId, payload),
    onSuccess: (task) => {
      setSelectedTask(task);
      refreshPlanAndValidation();
    }
  });
  const deleteTask = useMutation({
    mutationFn: api.deleteTask,
    onSuccess: () => {
      setSelectedTask(null);
      refreshPlanAndValidation();
    }
  });
  const createDependency = useMutation({
    mutationFn: ({ from_task_id, to_task_id }: { from_task_id: string; to_task_id: string }) => api.createDependency(activePlanId!, { from_task_id, to_task_id }),
    onSuccess: refreshPlanAndValidation
  });
  const deleteDependency = useMutation({
    mutationFn: api.deleteDependency,
    onSuccess: refreshPlanAndValidation
  });

  const selected = useMemo(() => {
    if (!selectedTask || !plan.data) return null;
    return plan.data.tasks.find((task) => task.id === selectedTask.id) ?? selectedTask;
  }, [plan.data, selectedTask]);
  const taskTitle = (taskId: string) => plan.data?.tasks.find((task) => task.id === taskId)?.title ?? taskId.slice(0, 8);

  if (!activePlanId || !plan.data) {
    return <div className="panel p-6 text-sm text-steel">No plan exists yet. Save a Task Contract and generate a template plan.</div>;
  }

  return (
    <div className="grid h-[calc(100vh-96px)] gap-4 xl:grid-cols-[300px_1fr_360px]">
      <aside className="panel overflow-auto p-4">
        <div className="font-mono text-[11px] uppercase text-limewire">Plan v{plan.data.version}</div>
        <h1 className="mt-2 font-display text-2xl font-black uppercase text-ink">DAG Editor</h1>
        <div className="mt-3"><StatusBadge status={plan.data.status} /></div>
        {plans.data && plans.data.length > 1 && (
          <>
            <label className="field-label">Plan Version</label>
            <select className="loom-input" value={plan.data.id} onChange={(event) => setSearchParams({ plan: event.target.value })}>
              {plans.data.map((item) => (
                <option key={item.id} value={item.id}>v{item.version} {item.status}</option>
              ))}
            </select>
          </>
        )}
        <p className="mt-4 text-sm leading-6 text-steel">{plan.data.summary}</p>
        <div className="mt-5 grid grid-cols-2 gap-3">
          <Metric label="Tasks" value={plan.data.tasks.length} />
          <Metric label="Edges" value={plan.data.dependencies.length} />
          <Metric label="High Risk" value={plan.data.tasks.filter((task) => ["HIGH", "CRITICAL"].includes(task.risk_level)).length} />
          <Metric label="Review" value={plan.data.tasks.filter((task) => task.human_review_required).length} />
        </div>
        <div className="mt-5 space-y-2">
          <button className="command-button w-full justify-center border-steel/40 text-ink" disabled={!editable} onClick={() => createTask.mutate()}>
            <Plus size={15} /> Add Task
          </button>
          <button className="command-button w-full justify-center border-limewire/50 text-limewire" onClick={() => validate.mutate()}>
            <ShieldCheck size={15} /> Validate DAG
          </button>
          <button className="command-button w-full justify-center border-amber-300/50 text-amber-200" disabled={!editable} onClick={() => submit.mutate()}>
            <GitPullRequest size={15} /> Submit Review
          </button>
          <button className="command-button w-full justify-center border-limewire/50 text-limewire" onClick={() => approve.mutate()}>
            <CheckCircle2 size={15} /> Approve Plan
          </button>
          {plan.data.status === "LOCKED" && (
            <button className="command-button w-full justify-center border-steel/40 text-ink" onClick={() => revise.mutate()}>
              <RefreshCw size={15} /> Revise Plan
            </button>
          )}
          <button className="command-button w-full justify-center border-ember/50 text-ember" disabled={!editable} onClick={() => reject.mutate()}>
            <XCircle size={15} /> Reject Plan
          </button>
        </div>
        {validation && (
          <div className="mt-5 border border-steel/20 p-3">
            <div className="mb-2 flex items-center gap-2 font-mono text-[11px] uppercase text-ink">
              <AlertTriangle size={14} /> Validation
            </div>
            <div className={validation.valid ? "text-sm text-limewire" : "text-sm text-ember"}>{validation.valid ? "Acyclic and executable." : "Plan has blockers."}</div>
            {[...validation.errors, ...validation.warnings].map((item) => (
              <div className="mt-2 text-xs text-steel" key={item}>{item}</div>
            ))}
          </div>
        )}
        <div className="mt-5 border border-steel/20 p-3">
          <div className="mb-2 font-mono text-[11px] uppercase text-limewire">Dependency Edges</div>
          <div className="space-y-2">
            {plan.data.dependencies.map((dependency) => (
              <div key={dependency.id} className="flex items-center justify-between gap-2 border border-steel/15 bg-carbon/40 p-2 text-xs text-steel">
                <span className="min-w-0 truncate">{taskTitle(dependency.from_task_id)} {"->"} {taskTitle(dependency.to_task_id)}</span>
                <button className="icon-button shrink-0 border-ember/40 text-ember" disabled={!editable} aria-label={`Remove dependency ${taskTitle(dependency.from_task_id)} to ${taskTitle(dependency.to_task_id)}`} onClick={() => deleteDependency.mutate(dependency.id)}>
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
            {!plan.data.dependencies.length && <div className="text-xs text-steel">No dependencies.</div>}
          </div>
        </div>
      </aside>
      <section className="panel overflow-hidden">
        <DagCanvas
          plan={plan.data}
          selectedTaskId={selected?.id ?? null}
          onSelectTask={setSelectedTask}
          onConnect={(from_task_id, to_task_id) => {
            if (editable) createDependency.mutate({ from_task_id, to_task_id });
          }}
          onDeleteDependency={(dependencyId) => {
            if (editable) deleteDependency.mutate(dependencyId);
          }}
          onMoveTask={(taskId, x, y) => updateTask.mutate({ taskId, payload: { position_x: x, position_y: y } })}
        />
      </section>
      <TaskInspector
        task={selected}
        locked={Boolean(locked)}
        onSave={(taskId, payload) => updateTask.mutate({ taskId, payload })}
        onDelete={(taskId) => deleteTask.mutate(taskId)}
      />
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="border border-steel/20 bg-carbon/50 p-3">
      <div className="font-mono text-[10px] uppercase text-steel">{label}</div>
      <div className="font-display text-2xl font-black text-ink">{value}</div>
    </div>
  );
}
