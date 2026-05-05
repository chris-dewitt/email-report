"""Parquet read/write helpers for FedLens bronze/silver/gold layers."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from fedlens.storage.paths import bronze_dir, gold_dir, silver_dir


# ---------- bronze ----------


def write_bronze_metadata(doc_id: str, doc_type: str, metadata: dict) -> Path:
    """Write document metadata JSON sidecar to bronze."""
    import json

    path = bronze_dir(doc_type) / f"{doc_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, default=str)
    return path


def write_bronze_html(doc_id: str, doc_type: str, html: str) -> Path:
    """Write raw HTML to bronze."""
    path = bronze_dir(doc_type) / f"{doc_id}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def read_bronze_html(doc_id: str, doc_type: str) -> str | None:
    """Read raw HTML from bronze."""
    path = bronze_dir(doc_type) / f"{doc_id}.html"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


# ---------- silver ----------


def write_silver(df: pl.DataFrame, name: str, sub: str = "parsed") -> Path:
    """Write a DataFrame to the silver layer."""
    path = silver_dir(sub) / f"{name}.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path)
    return path


def read_silver(name: str, sub: str = "parsed") -> pl.DataFrame | None:
    """Read a DataFrame from the silver layer."""
    path = silver_dir(sub) / f"{name}.parquet"
    if not path.exists():
        return None
    return pl.read_parquet(path)


# ---------- gold ----------


def write_gold(df: pl.DataFrame, name: str, sub: str = "sentiment") -> Path:
    """Write a DataFrame to the gold layer."""
    path = gold_dir(sub) / f"{name}.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path)
    return path


def read_gold(name: str, sub: str = "sentiment") -> pl.DataFrame | None:
    """Read a DataFrame from the gold layer."""
    path = gold_dir(sub) / f"{name}.parquet"
    if not path.exists():
        return None
    return pl.read_parquet(path)
