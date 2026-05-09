"""Semantic drift detection — track how Fed language changes over time."""

from __future__ import annotations

import numpy as np
import polars as pl

from fedlens.storage.paths import gold_dir, silver_dir


def compute_document_embeddings() -> pl.DataFrame | None:
    """Compute average embedding per document from chunk embeddings.

    Returns DataFrame: doc_id, date, doc_type, embedding (list[float])
    """
    emb_path = gold_dir("embeddings") / "chunk_embeddings.parquet"
    if not emb_path.exists():
        return None

    emb_df = pl.read_parquet(emb_path)

    # Get chunk metadata to link chunks to documents
    parsed_dir = silver_dir("parsed")
    all_meta = []
    for pq in parsed_dir.glob("*.parquet"):
        df = pl.read_parquet(pq).select(["chunk_id", "doc_id", "date", "doc_type"])
        all_meta.append(df)

    if not all_meta:
        return None

    meta_df = pl.concat(all_meta)

    # Join embeddings with metadata
    joined = emb_df.join(meta_df, on="chunk_id", how="inner")

    # Average embeddings per document
    doc_embeddings = []
    for doc_id in joined["doc_id"].unique().to_list():
        doc_rows = joined.filter(pl.col("doc_id") == doc_id)
        emb_list = doc_rows["embedding"].to_list()
        avg_emb = np.mean([np.array(e) for e in emb_list], axis=0).tolist()

        doc_embeddings.append({
            "doc_id": doc_id,
            "date": doc_rows["date"][0],
            "doc_type": doc_rows["doc_type"][0],
            "embedding": avg_emb,
        })

    return pl.DataFrame(doc_embeddings).sort("date")


def compute_drift_series(doc_type: str | None = None) -> pl.DataFrame | None:
    """Compute semantic drift between consecutive documents.

    Returns DataFrame: date, doc_id, prev_doc_id, cosine_sim, drift_score,
                       rolling_4_drift
    """
    doc_emb = compute_document_embeddings()
    if doc_emb is None or doc_emb.is_empty():
        return None

    if doc_type:
        doc_emb = doc_emb.filter(pl.col("doc_type") == doc_type)

    doc_emb = doc_emb.sort("date")

    if len(doc_emb) < 2:
        return None

    rows = []
    embeddings = doc_emb["embedding"].to_list()
    doc_ids = doc_emb["doc_id"].to_list()
    dates = doc_emb["date"].to_list()

    for i in range(1, len(embeddings)):
        prev_emb = np.array(embeddings[i - 1])
        curr_emb = np.array(embeddings[i])

        # Cosine similarity (embeddings are already normalized)
        cos_sim = float(np.dot(prev_emb, curr_emb) / (
            np.linalg.norm(prev_emb) * np.linalg.norm(curr_emb) + 1e-8
        ))

        rows.append({
            "date": dates[i],
            "doc_id": doc_ids[i],
            "prev_doc_id": doc_ids[i - 1],
            "cosine_sim": round(cos_sim, 6),
            "drift_score": round(1.0 - cos_sim, 6),
        })

    drift_df = pl.DataFrame(rows)

    # Add rolling 4-meeting average drift
    drift_df = drift_df.with_columns(
        pl.col("drift_score")
        .rolling_mean(window_size=4, min_periods=1)
        .alias("rolling_4_drift")
    )

    return drift_df


def build_drift_features() -> None:
    """Compute and save drift features to gold layer."""
    from rich.console import Console

    console = Console()

    for dtype in ("statement", "minutes", "speech", "pressconf"):
        drift_df = compute_drift_series(doc_type=dtype)
        if drift_df is not None and not drift_df.is_empty():
            out_path = gold_dir("drift")
            out_path.mkdir(parents=True, exist_ok=True)
            drift_df.write_parquet(out_path / f"{dtype}_drift.parquet")
            console.print(f"  Drift/{dtype}: [yellow]{len(drift_df)}[/yellow] records")

    # Also compute overall drift
    drift_all = compute_drift_series()
    if drift_all is not None and not drift_all.is_empty():
        out_path = gold_dir("drift")
        drift_all.write_parquet(out_path / "all_drift.parquet")
        console.print(f"  Drift/all: [yellow]{len(drift_all)}[/yellow] records")
