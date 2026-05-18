import type { LedgerEvent } from "../types/domain";

export function EventTimeline({ events }: { events: LedgerEvent[] }) {
  return (
    <div className="space-y-2">
      {events.slice(0, 18).map((event) => (
        <div key={event.id} className="grid grid-cols-[118px_1fr] gap-3 border-l border-steel/20 pl-3">
          <time className="font-mono text-[11px] text-steel">{new Date(event.created_at).toLocaleTimeString()}</time>
          <div>
            <div className="font-mono text-[11px] uppercase text-ink">{event.event_type}</div>
            <div className="truncate text-xs text-steel">{event.task_id ?? event.plan_id ?? event.run_id}</div>
          </div>
        </div>
      ))}
      {!events.length && <div className="text-sm text-steel">No ledger events yet.</div>}
    </div>
  );
}

