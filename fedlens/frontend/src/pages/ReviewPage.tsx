import { useState } from "react";
import { useReviews, useApproveReview, useRejectReview } from "@/api/hooks";
import { formatDate } from "@/lib/utils";
import { ClipboardCheck, CheckCircle, XCircle, Clock } from "lucide-react";

export function ReviewPage() {
  const [filter, setFilter] = useState<string | undefined>("pending");
  const { data, isLoading } = useReviews(filter);
  const approveMutation = useApproveReview();
  const rejectMutation = useRejectReview();
  const [comment, setComment] = useState("");

  const handleApprove = (reviewId: string) => {
    approveMutation.mutate({ reviewId, comment: comment || undefined });
    setComment("");
  };

  const handleReject = (reviewId: string) => {
    rejectMutation.mutate({ reviewId, comment: comment || undefined });
    setComment("");
  };

  const statusIcon = (status: string) => {
    switch (status) {
      case "approved": return <CheckCircle size={16} className="text-fed-green" />;
      case "rejected": return <XCircle size={16} className="text-fed-red" />;
      default: return <Clock size={16} className="text-fed-yellow" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-fed-text">Review Queue</h2>
          <p className="text-sm text-fed-muted mt-1">Human-in-the-loop review for agent outputs</p>
        </div>
        <div className="flex gap-2">
          {[
            { value: "pending", label: "Pending" },
            { value: undefined, label: "All" },
          ].map((opt) => (
            <button
              key={opt.label}
              onClick={() => setFilter(opt.value)}
              className={`rounded px-3 py-1 text-xs font-medium transition ${
                filter === opt.value ? "bg-fed-accent text-white" : "text-fed-muted hover:text-fed-text"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <p className="text-sm text-fed-muted">Loading reviews...</p>
      ) : !data?.reviews.length ? (
        <div className="flex flex-col items-center justify-center py-16 text-fed-muted">
          <ClipboardCheck size={48} className="mb-3 opacity-30" />
          <p className="text-sm">No reviews {filter === "pending" ? "pending" : "found"}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {data.reviews.map((review) => (
            <div
              key={review.review_id}
              className="rounded-lg border border-fed-border bg-fed-surface p-4"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  {statusIcon(review.status)}
                  <span className="text-sm font-medium text-fed-text">{review.agent_name}</span>
                  <span className="text-xs text-fed-muted">
                    {formatDate(review.submitted_at)}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-fed-muted">
                    Confidence: {(review.confidence * 100).toFixed(0)}%
                  </span>
                  <span className={
                    review.status === "approved" ? "text-fed-green font-medium" :
                    review.status === "rejected" ? "text-fed-red font-medium" :
                    "text-fed-yellow font-medium"
                  }>
                    {review.status}
                  </span>
                </div>
              </div>

              {review.output_preview && (
                <p className="text-sm text-fed-text bg-fed-bg/50 rounded p-3 mb-3">
                  {review.output_preview}
                </p>
              )}

              {review.reviewer_comment && (
                <p className="text-xs text-fed-muted italic mb-3">
                  Comment: {review.reviewer_comment}
                </p>
              )}

              {review.status === "pending" && (
                <div className="flex items-center gap-2 mt-2">
                  <input
                    type="text"
                    placeholder="Optional comment..."
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    className="flex-1 rounded border border-fed-border bg-fed-bg px-3 py-1.5 text-sm text-fed-text placeholder-fed-muted focus:border-fed-accent focus:outline-none"
                  />
                  <button
                    onClick={() => handleApprove(review.review_id)}
                    disabled={approveMutation.isPending}
                    className="flex items-center gap-1 rounded bg-fed-green/20 px-3 py-1.5 text-xs font-medium text-fed-green hover:bg-fed-green/30 disabled:opacity-50"
                  >
                    <CheckCircle size={14} /> Approve
                  </button>
                  <button
                    onClick={() => handleReject(review.review_id)}
                    disabled={rejectMutation.isPending}
                    className="flex items-center gap-1 rounded bg-fed-red/20 px-3 py-1.5 text-xs font-medium text-fed-red hover:bg-fed-red/30 disabled:opacity-50"
                  >
                    <XCircle size={14} /> Reject
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
