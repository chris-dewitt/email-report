"""FastAPI dependency injection — DuckDB connection, config, etc."""

from __future__ import annotations

from functools import lru_cache

from atlas.config import get_settings, AtlasSettings
from atlas.storage.duckdb_store import DuckDBStore


@lru_cache(maxsize=1)
def get_db() -> DuckDBStore:
    """Get or create the DuckDB store singleton."""
    db = DuckDBStore()
    db.register_views()
    return db


def get_config() -> AtlasSettings:
    return get_settings()
