import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { ReviewPacket } from "../components/ReviewPacket";

export function ReviewQueuePage() {
  const { runId = "" } = useParams();
  const queryClient = useQueryClient();
  const reviews = useQuery({ queryKey: ["reviews", "pending"], queryFn: () => api.listReviews("PENDING"), refetchInterval: 2000 });
  const visibleReviews = reviews.data?.filter((review) => review.run_id === runId) ?? [];
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["reviews", "pending"] });
    queryClient.invalidateQueries({ queryKey: ["status", runId] });
  };
  const approve = useMutation({ mutationFn: (reviewId: string) => api.approveReview(reviewId), onSuccess: invalidate });
  const reject = useMutation({ mutationFn: (reviewId: string) => api.rejectReview(reviewId), onSuccess: invalidate });
  const changes = useMutation({ mutationFn: (reviewId: string) => api.requestChanges(reviewId), onSuccess: invalidate });

  return (
    <div className="grid gap-5 xl:grid-cols-[320px_1fr]">
      <aside className="panel p-5">
        <div className="font-mono text-[11px] uppercase text-limewire">Human Review</div>
        <h1 className="mt-2 font-display text-3xl font-black uppercase text-ink">Decision Queue</h1>
        <p className="mt-3 text-sm leading-6 text-steel">Review packets are compact summaries generated from policy gates, not raw traces.</p>
        <div className="mt-6 border border-steel/20 p-4">
          <div className="font-mono text-[10px] uppercase text-steel">Pending</div>
          <div className="font-display text-4xl font-black text-limewire">{visibleReviews.length}</div>
        </div>
      </aside>
      <section className="space-y-4">
        {visibleReviews.map((review) => (
          <ReviewPacket
            key={review.id}
            review={review}
            onApprove={() => approve.mutate(review.id)}
            onReject={() => reject.mutate(review.id)}
            onChanges={() => changes.mutate(review.id)}
          />
        ))}
        {!visibleReviews.length && <div className="panel p-6 text-sm text-steel">No pending review packets for this run.</div>}
      </section>
    </div>
  );
}
