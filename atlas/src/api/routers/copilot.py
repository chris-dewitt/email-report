"""Copilot/briefing endpoint — macro narrative generation via local LLM."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from atlas.models.copilot import BriefingRequest, BriefingResponse

router = APIRouter()


@router.post("/copilot/briefing", response_model=BriefingResponse)
async def generate_briefing_endpoint(request: BriefingRequest) -> BriefingResponse:
    """Generate a macro briefing using the local LLM copilot."""
    try:
        from atlas.copilot.briefing import generate_briefing

        result = generate_briefing(
            question=request.question,
            lookback_days=request.lookback_days,
        )

        from atlas.models.copilot import Citation
        citations = [Citation(series_id=c) for c in result.get("citations", [])]

        return BriefingResponse(
            summary=result["summary"],
            citations=citations,
            model_used=result.get("model_used", ""),
            generated_at=result.get("generated_at"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Copilot unavailable: {e}. Is Ollama running?",
        )
