"""Briefing/copilot endpoint for FedLens."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class BriefingRequest(BaseModel):
    question: str | None = None
    doc_id: str | None = None


@router.post("/briefing")
async def generate_briefing(request: BriefingRequest):
    """Generate a policy briefing using RAG + local LLM."""
    try:
        from fedlens.agents.briefing_agent import BriefingAgent

        agent = BriefingAgent()
        trace = agent.run(question=request.question, doc_id=request.doc_id)

        return {
            "briefing": trace.output.get("briefing", ""),
            "citations": [
                {"doc_id": c.doc_id, "text_excerpt": c.text_excerpt, "score": c.relevance_score}
                for c in trace.citations
            ],
            "confidence": trace.confidence,
            "approval_status": trace.approval_status,
            "steps": len(trace.steps),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Briefing generation failed: {e}")
