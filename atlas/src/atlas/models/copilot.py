"""Pydantic models for copilot/briefing contracts."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class BriefingRequest(BaseModel):
    """Request for a macro briefing from the copilot."""
    question: str | None = None  # None = default "what changed this week"
    lookback_days: int = 7


class Citation(BaseModel):
    """A citation to a specific series or feature in the briefing."""
    series_id: str
    context: str = ""


class BriefingResponse(BaseModel):
    """Response from the copilot with narrative + citations."""
    summary: str
    citations: list[Citation] = []
    model_used: str = ""
    prompt_tokens: int = 0
    response_tokens: int = 0
    generated_at: datetime | None = None
