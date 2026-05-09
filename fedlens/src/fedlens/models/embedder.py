"""Embedding generation and FAISS index building for FedLens."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import polars as pl
from rich.console import Console
from rich.progress import track

from fedlens.config import get_settings
from fedlens.models.vector_store import FAISSStore
from fedlens.storage.paths import silver_dir, gold_dir

console = Console()


class ChunkEmbedder:
    """Generate embeddings using sentence-transformers (local, no API)."""

    def __init__(self, model_name: str | None = None):
        settings = get_settings().embedding
        self._model_name = model_name or settings.model_name
        self._device = settings.device
        self._batch_size = settings.batch_size
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            console.print(f"  Loading embedding model [cyan]{self._model_name}[/cyan]...")
            self._model = SentenceTransformer(self._model_name, device=self._device)
        return self._model

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Embed a batch of texts. Returns (N, dim) float32 array, L2-normalized."""
        model = self._load_model()
        embeddings = model.encode(
            texts,
            batch_size=self._batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embeddings.astype(np.float32)

    def embed_single(self, text: str) -> np.ndarray:
        """Embed a single text. Returns (dim,) float32 array, L2-normalized."""
        model = self._load_model()
        embedding = model.encode(
            [text],
            normalize_embeddings=True,
        )
        return embedding[0].astype(np.float32)


@lru_cache(maxsize=1)
def get_embedder() -> ChunkEmbedder:
    """Get or create the singleton embedder."""
    return ChunkEmbedder()


def build_embeddings(rebuild: bool = False) -> None:
    """Generate embeddings for all chunks and build FAISS index."""
    store = FAISSStore()

    if store.is_built and not rebuild:
        console.print("[yellow]FAISS index already exists. Use --rebuild to regenerate.[/yellow]")
        return

    # Load all chunks from silver
    parsed_dir = silver_dir("parsed")
    if not parsed_dir.exists():
        console.print("[red]No parsed chunks found. Run 'fedlens ingest' first.[/red]")
        return

    all_dfs = []
    for pq in parsed_dir.glob("*.parquet"):
        all_dfs.append(pl.read_parquet(pq))

    if not all_dfs:
        console.print("[red]No parquet files found in silver/parsed.[/red]")
        return

    chunks_df = pl.concat(all_dfs)
    console.print(f"\n[bold cyan]Embedding {len(chunks_df)} chunks...[/bold cyan]")

    embedder = get_embedder()
    texts = chunks_df["text"].to_list()
    chunk_ids = chunks_df["chunk_id"].to_list()

    # Embed in batches with progress
    batch_size = get_settings().embedding.batch_size
    all_embeddings = []

    for i in track(range(0, len(texts), batch_size), description="Embedding"):
        batch = texts[i : i + batch_size]
        batch_emb = embedder.embed_batch(batch)
        all_embeddings.append(batch_emb)

    embeddings = np.vstack(all_embeddings)
    console.print(f"  Embeddings shape: [yellow]{embeddings.shape}[/yellow]")

    # Build FAISS index
    console.print("  Building FAISS index...")
    store.build_index(embeddings, chunk_ids)
    console.print(f"  Index saved: [yellow]{store.size}[/yellow] vectors")

    # Save embeddings to gold layer for DuckDB access
    emb_path = gold_dir("embeddings")
    emb_path.mkdir(parents=True, exist_ok=True)

    # Store as parquet (chunk_id + embedding as list)
    emb_df = pl.DataFrame({
        "chunk_id": chunk_ids,
        "embedding": [emb.tolist() for emb in embeddings],
    })
    emb_df.write_parquet(emb_path / "chunk_embeddings.parquet")

    console.print("\n[bold green]Embedding pipeline complete.[/bold green]")
