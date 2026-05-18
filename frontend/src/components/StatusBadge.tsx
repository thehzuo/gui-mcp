import type { TaskStatus } from "../types/domain";

const toneByStatus: Record<string, string> = {
  DRAFT: "border-steel/30 text-steel",
  PLANNING: "border-steel/30 text-steel",
  AWAITING_PLAN_REVIEW: "border-limewire/50 text-limewire",
  PLAN_APPROVED: "border-limewire/50 text-limewire",
  READY: "border-limewire/40 text-limewire",
  BLOCKED: "border-ember/50 text-ember",
  AWAITING_REVIEW: "border-amber-300/50 text-amber-200",
  PENDING: "border-amber-300/50 text-amber-200",
  QUEUED: "border-cyan-300/50 text-cyan-200",
  RUNNING: "border-cyan-300/50 text-cyan-200",
  VERIFYING: "border-cyan-300/50 text-cyan-200",
  SUCCEEDED: "border-limewire/60 text-limewire",
  COMPLETED: "border-limewire/60 text-limewire",
  FAILED: "border-ember/60 text-ember",
  CANCELED: "border-zinc-500 text-zinc-400",
  NEEDS_HUMAN: "border-amber-300/50 text-amber-200"
};

export function StatusBadge({ status }: { status: string | TaskStatus }) {
  return (
    <span className={`inline-flex h-6 items-center border px-2 font-mono text-[11px] uppercase tracking-normal ${toneByStatus[status] ?? "border-steel/30 text-steel"}`}>
      {status.split("_").join(" ")}
    </span>
  );
}
