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
          <dd className="text-ink">{String(packet.verifier_coverage ?? "n/a")}</dd>
        </div>
        <div>
          <dt className="font-mono text-[10px] uppercase text-steel">Recommendation</dt>
          <dd className="text-ink">{String(packet.recommended_decision ?? "Review packet")}</dd>
        </div>
      </dl>
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

