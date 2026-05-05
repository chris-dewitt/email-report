"""Document endpoints for FedLens."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
import polars as pl

from fedlens.storage.paths import silver_dir

router = APIRouter()


@router.get("/documents")
async def list_documents(doc_type: str | None = None):
    """List all ingested documents with metadata."""
    meta_dir = silver_dir("metadata")
    if not meta_dir.exists():
        return {"documents": [], "total": 0}

    all_dfs = []
    for pq in meta_dir.glob("*.parquet"):
        df = pl.read_parquet(pq)
        if doc_type:
            df = df.filter(pl.col("doc_type") == doc_type)
        all_dfs.append(df)

    if not all_dfs:
        return {"documents": [], "total": 0}

    combined = pl.concat(all_dfs).sort("date", descending=True)

    # Join with sentiment if available
    sent_path = silver_dir("..") / "gold" / "sentiment" / "statement.parquet"
    # Normalize path
    from fedlens.storage.paths import gold_dir

    sent_path = gold_dir("sentiment") / "statement.parquet"
    if sent_path.exists():
        sent_df = pl.read_parquet(sent_path).select(["doc_id", "net_score", "hawkish_count", "dovish_count"])
        combined = combined.join(sent_df, on="doc_id", how="left")

    docs = combined.to_dicts()
    return {"documents": docs, "total": len(docs)}


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get a document with its chunks."""
    parsed_dir = silver_dir("parsed")
    for pq in parsed_dir.glob("*.parquet"):
        df = pl.read_parquet(pq)
        matched = df.filter(pl.col("doc_id") == doc_id)
        if not matched.is_empty():
            chunks = matched.sort("chunk_index").to_dicts()
            return {
                "doc_id": doc_id,
                "chunks": chunks,
                "total_chunks": len(chunks),
            }

    raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
