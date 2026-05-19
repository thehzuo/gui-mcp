import { Check, FilePenLine, X } from "lucide-react";
import type { ReviewRecord } from "../types/domain";

interface ReviewPacketProps {
  review: ReviewRecord;
  onApprove: () => void;
  onReject: () => void;
  onChanges: () => void;
}

export function ReviewPacket({ review, onApprove, onReject, onChanges }: ReviewPacketProps) {
  const packet = review.packet_json;
  const title = String(packet.task_title ?? packet.plan_summary ?? review.review_type);
  const reason = String(packet.why_review_is_required ?? review.reason ?? "Review required.");
  const dependencies = asList(packet.dependencies);
  const downstream = asList(packet.affected_downstream_tasks);
  const expectedOutputs = asList(packet.expected_outputs);

  return (
    <article className="border border-steel/20 bg-panel/90 p-4 shadow-[0_0_0_1px_rgba(213,255,91,0.04)]">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <div className="font-mono text-[11px] uppercase text-limewire">{review.review_type}</div>
          <h3 className="mt-1 font-display text-lg font-semibold text-ink">{title}</h3>
          <p className="mt-2 text-sm text-steel">{reason}</p>
        </div>
        <span className="border border-amber-300/50 px-2 py-1 font-mono text-[11px] uppercase text-amber-200">{review.status}</span>
      </div>
      <dl className="grid gap-3 text-sm sm:grid-cols-3">
        <div>
          <dt className="font-mono text-[10px] uppercase text-steel">Risk</dt>
          <dd className="text-ink">{String(packet.risk_level ?? packet.high_risk_task_count ?? "n/a")}</dd>
        </div>
        <div>
          <dt className="font-mono text-[10px] uppercase text-steel">Verifier</dt>
          <dd className="text-ink">{formatPacketValue(packet.verifier_coverage ?? "n/a")}</dd>
        </div>
        <div>
          <dt className="font-mono text-[10px] uppercase text-steel">Recommendation</dt>
          <dd className="text-ink">{String(packet.recommended_decision ?? "Review packet")}</dd>
        </div>
        <div>
          <dt className="font-mono text-[10px] uppercase text-steel">Execution</dt>
          <dd className="text-ink">{formatPacketValue(packet.proposed_execution_mode ?? "n/a")}</dd>
        </div>
        <div>
          <dt className="font-mono text-[10px] uppercase text-steel">Policy</dt>
          <dd className="text-ink">{String(packet.policy_decision ?? "Plan review")}</dd>
        </div>
        <div>
          <dt className="font-mono text-[10px] uppercase text-steel">Reversibility</dt>
          <dd className="text-ink">{String(packet.reversibility ?? "n/a")}</dd>
        </div>
      </dl>
      <PacketList title="Dependencies" values={dependencies} />
      <PacketList title="Expected Outputs" values={expectedOutputs} />
      <PacketList title="Affected Downstream" values={downstream} />
      <div className="mt-4 flex flex-wrap gap-2">
        <button className="command-button border-limewire/50 text-limewire" onClick={onApprove}>
          <Check size={15} /> Approve
        </button>
        <button className="command-button border-steel/40 text-steel" onClick={onChanges}>
          <FilePenLine size={15} /> Changes
        </button>
        <button className="command-button border-ember/50 text-ember" onClick={onReject}>
          <X size={15} /> Reject
        </button>
      </div>
    </article>
  );
}

function asList(value: unknown): string[] {
  if (!value) return [];
  if (Array.isArray(value)) return value.map((item) => formatPacketValue(item));
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>).map(([key, item]) => `${key}: ${formatPacketValue(item)}`);
  }
  return [String(value)];
}

function formatPacketValue(value: unknown): string {
  if (Array.isArray(value)) return value.map((item) => formatPacketValue(item)).join(", ");
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    if ("from_title" in record || "to_title" in record) return `${String(record.from_title ?? record.from_task_id)} -> ${String(record.to_title ?? record.to_task_id)}`;
    return Object.entries(record).map(([key, item]) => `${key}: ${formatPacketValue(item)}`).join("; ");
  }
  return String(value ?? "n/a");
}

function PacketList({ title, values }: { title: string; values: string[] }) {
  if (!values.length) return null;
  return (
    <div className="mt-4">
      <div className="mb-2 font-mono text-[10px] uppercase text-steel">{title}</div>
      <div className="flex flex-wrap gap-2">
        {values.map((value) => (
          <span key={`${title}-${value}`} className="max-w-full break-words border border-steel/20 bg-carbon/50 px-2 py-1 text-xs text-steel">{value}</span>
        ))}
      </div>
    </div>
  );
}
