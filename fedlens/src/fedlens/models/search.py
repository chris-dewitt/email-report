"""High-level semantic search combining FAISS + metadata filtering."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import polars as pl

from fedlens.models.vector_store import FAISSStore


@dataclass
class SearchHit:
    """Enriched search result with chunk text and metadata."""

    chunk_id: str
    doc_id: str
    doc_type: str
    date: date
    section_heading: str
    text: str
    score: float
    rank: int


def semantic_search(
    query: str,
    k: int = 10,
    doc_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[SearchHit]:
    """Run semantic search with optional metadata filters.

    1. Embed the query
    2. Search FAISS for top candidates (over-fetch for filtering)
    3. Join with chunk metadata
    4. Apply post-filters
    5. Return enriched results
    """
    from fedlens.models.embedder import get_embedder

    embedder = get_embedder()
    query_vec = embedder.embed_single(query)

    store = FAISSStore()
    # Over-fetch to allow for post-filtering
    fetch_k = min(k * 5, store.size) if store.size > 0 else k
    raw_results = store.search(query_vec, k=fetch_k)

    if not raw_results:
        return []

    # Load chunk metadata
    chunk_ids = [r.chunk_id for r in raw_results]
    scores = {r.chunk_id: r.score for r in raw_results}

    # Read silver parsed data to get chunk text + metadata
    from fedlens.storage.paths import silver_dir

    parsed_dir = silver_dir("parsed")
    all_chunks = []
    if parsed_dir.exists():
        for pq in parsed_dir.glob("*.parquet"):
            df = pl.read_parquet(pq)
            matched = df.filter(pl.col("chunk_id").is_in(chunk_ids))
            if not matched.is_empty():
                all_chunks.append(matched)

    if not all_chunks:
        return []

    chunks_df = pl.concat(all_chunks)

    # Apply filters
    if doc_type:
        chunks_df = chunks_df.filter(pl.col("doc_type") == doc_type)
    if date_from:
        chunks_df = chunks_df.filter(pl.col("date") >= date_from)
    if date_to:
        chunks_df = chunks_df.filter(pl.col("date") <= date_to)

    # Build results
    hits = []
    for row in chunks_df.iter_rows(named=True):
        cid = row["chunk_id"]
        if cid in scores:
            hits.append(SearchHit(
                chunk_id=cid,
                doc_id=row["doc_id"],
                doc_type=row["doc_type"],
                date=row["date"],
                section_heading=row["section_heading"],
                text=row["text"],
                score=scores[cid],
                rank=0,
            ))

    # Sort by score descending, assign ranks, limit to k
    hits.sort(key=lambda h: h.score, reverse=True)
    for i, h in enumerate(hits):
        h.rank = i
    return hits[:k]
