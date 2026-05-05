"""Health check endpoint for FedLens."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from fedlens.storage.paths import bronze_dir, silver_dir, gold_dir, vector_dir

router = APIRouter()


@router.get("/health")
async def health():
    """Return system health: document counts, index status, Ollama status."""
    # Count bronze documents
    doc_counts = {}
    for dtype in ("statements", "minutes", "speeches", "pressconf"):
        d = bronze_dir(dtype)
        doc_counts[dtype] = len(list(d.glob("*.html"))) if d.exists() else 0

    total_docs = sum(doc_counts.values())

    # Check FAISS index
    faiss_path = vector_dir() / "faiss.index"
    index_built = faiss_path.exists()

    # Check Ollama
    try:
        from fedlens.copilot.ollama_client import OllamaClient

        ollama_ok = OllamaClient().is_available()
    except Exception:
        ollama_ok = False

    # Gold layer counts
    gold_counts = {}
    for sub in ("sentiment", "event_study", "topics", "drift"):
        d = gold_dir(sub)
        gold_counts[sub] = len(list(d.glob("*.parquet"))) if d.exists() else 0

    return {
        "status": "ok",
        "total_documents": total_docs,
        "documents": doc_counts,
        "index_built": index_built,
        "ollama_available": ollama_ok,
        "gold_layers": gold_counts,
    }
