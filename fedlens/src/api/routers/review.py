"""HITL review queue endpoints for FedLens."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from fedlens.agents.hitl import ReviewQueue

router = APIRouter()
_queue = ReviewQueue()


@router.get("/reviews")
async def list_reviews(status: str | None = None):
    """List all review items, optionally filtered by status."""
    if status == "pending":
        items = _queue.list_pending()
    else:
        items = _queue.list_all()

    return {
        "reviews": [
            {
                "review_id": item.review_id,
                "agent_name": item.trace.get("agent_name", ""),
                "submitted_at": item.submitted_at,
                "reviewed_at": item.reviewed_at,
                "status": item.status,
                "reviewer_comment": item.reviewer_comment,
                "confidence": item.trace.get("confidence", 0),
                "output_preview": str(item.trace.get("output", {}).get("briefing", ""))[:200],
            }
            for item in items
        ],
        "total": len(items),
    }


class ReviewAction(BaseModel):
    comment: str = ""


@router.post("/reviews/{review_id}/approve")
async def approve_review(review_id: str, action: ReviewAction):
    """Approve a pending review."""
    if _queue.approve(review_id, action.comment):
        return {"status": "approved", "review_id": review_id}
    raise HTTPException(status_code=404, detail=f"Review {review_id} not found")


@router.post("/reviews/{review_id}/reject")
async def reject_review(review_id: str, action: ReviewAction):
    """Reject a pending review."""
    if _queue.reject(review_id, action.comment):
        return {"status": "rejected", "review_id": review_id}
    raise HTTPException(status_code=404, detail=f"Review {review_id} not found")
