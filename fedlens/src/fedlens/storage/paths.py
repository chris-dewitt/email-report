"""Canonical data directory layout for FedLens."""

from __future__ import annotations

from pathlib import Path

from fedlens.config import get_settings

# ---------- root ----------


def data_root() -> Path:
    return Path(get_settings().data_dir).resolve()


# ---------- bronze ----------


def bronze_dir(doc_type: str | None = None) -> Path:
    base = data_root() / "bronze"
    return base / doc_type if doc_type else base


# ---------- silver ----------


def silver_dir(sub: str = "parsed") -> Path:
    return data_root() / "silver" / sub


# ---------- gold ----------


def gold_dir(sub: str = "sentiment") -> Path:
    return data_root() / "gold" / sub


# ---------- vector ----------


def vector_dir() -> Path:
    return data_root() / "vector"


# ---------- reviews ----------


def reviews_dir() -> Path:
    return data_root() / "reviews"


# ---------- duckdb ----------


def duckdb_path() -> Path:
    return data_root() / "fedlens.duckdb"


# ---------- helpers ----------

ALL_DIRS = [
    lambda: bronze_dir("statements"),
    lambda: bronze_dir("minutes"),
    lambda: bronze_dir("speeches"),
    lambda: bronze_dir("pressconf"),
    lambda: silver_dir("parsed"),
    lambda: silver_dir("metadata"),
    lambda: gold_dir("embeddings"),
    lambda: gold_dir("sentiment"),
    lambda: gold_dir("event_study"),
    lambda: gold_dir("topics"),
    lambda: gold_dir("drift"),
    lambda: vector_dir(),
    lambda: reviews_dir(),
]


def ensure_dirs() -> None:
    """Create all data directories if they don't exist."""
    for dir_fn in ALL_DIRS:
        dir_fn().mkdir(parents=True, exist_ok=True)
