"""FAISS vector store for semantic search."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
import polars as pl

from fedlens.storage.paths import vector_dir


@dataclass
class SearchResult:
    """A single search result from FAISS."""

    chunk_id: str
    score: float
    rank: int


class FAISSStore:
    """FAISS-backed vector store with chunk ID mapping."""

    def __init__(self, index_path: Path | None = None):
        self._index_path = index_path or (vector_dir() / "faiss.index")
        self._id_map_path = self._index_path.parent / "id_map.parquet"
        self._index: faiss.IndexFlatIP | None = None
        self._chunk_ids: list[str] = []

    @property
    def is_built(self) -> bool:
        return self._index_path.exists()

    @property
    def size(self) -> int:
        if self._index is not None:
            return self._index.ntotal
        return 0

    def build_index(self, embeddings: np.ndarray, chunk_ids: list[str]) -> None:
        """Build a new FAISS index from embeddings.

        Args:
            embeddings: (N, dim) float32 array, L2-normalized.
            chunk_ids: list of chunk_id strings, one per row.
        """
        assert len(embeddings) == len(chunk_ids), "Embeddings and chunk_ids must match"
        assert embeddings.dtype == np.float32, "Embeddings must be float32"

        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)  # inner product = cosine sim for normalized vectors
        self._index.add(embeddings)
        self._chunk_ids = list(chunk_ids)

        self.save()

    def search(self, query_embedding: np.ndarray, k: int = 10) -> list[SearchResult]:
        """Search the index for the k nearest neighbors.

        Args:
            query_embedding: (1, dim) or (dim,) float32 array, L2-normalized.
            k: number of results to return.

        Returns:
            List of SearchResult ordered by descending score.
        """
        self._ensure_loaded()

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        k = min(k, self._index.ntotal)
        scores, indices = self._index.search(query_embedding, k)

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < 0:  # FAISS returns -1 for missing
                continue
            results.append(SearchResult(
                chunk_id=self._chunk_ids[idx],
                score=float(score),
                rank=rank,
            ))

        return results

    def save(self) -> None:
        """Persist index and ID map to disk."""
        if self._index is None:
            return

        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(self._index_path))

        id_df = pl.DataFrame({
            "position": list(range(len(self._chunk_ids))),
            "chunk_id": self._chunk_ids,
        })
        id_df.write_parquet(self._id_map_path)

    def load(self) -> None:
        """Load index and ID map from disk."""
        if not self._index_path.exists():
            raise FileNotFoundError(f"FAISS index not found at {self._index_path}")

        self._index = faiss.read_index(str(self._index_path))

        if self._id_map_path.exists():
            id_df = pl.read_parquet(self._id_map_path)
            self._chunk_ids = id_df.sort("position")["chunk_id"].to_list()
        else:
            self._chunk_ids = [str(i) for i in range(self._index.ntotal)]

    def _ensure_loaded(self) -> None:
        if self._index is None:
            self.load()
