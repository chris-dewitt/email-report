"""Semantic search endpoint for FedLens."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    k: int = 10
    doc_type: str | None = None
    date_from: str | None = None
    date_to: str | None = None


@router.post("/search")
async def search_documents(request: SearchRequest):
    """Semantic search across Fed documents."""
    from fedlens.models.search import semantic_search

    date_from = date.fromisoformat(request.date_from) if request.date_from else None
    date_to = date.fromisoformat(request.date_to) if request.date_to else None

    results = semantic_search(
        query=request.query,
        k=request.k,
        doc_type=request.doc_type,
        date_from=date_from,
        date_to=date_to,
    )

    return {
        "results": [
            {
                "chunk_id": r.chunk_id,
                "doc_id": r.doc_id,
                "doc_type": r.doc_type,
                "date": r.date.isoformat() if hasattr(r.date, 'isoformat') else str(r.date),
                "section_heading": r.section_heading,
                "text": r.text,
                "score": r.score,
                "rank": r.rank,
            }
            for r in results
        ],
        "total": len(results),
        "query": request.query,
    }
