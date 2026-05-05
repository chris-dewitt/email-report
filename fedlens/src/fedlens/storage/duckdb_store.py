"""DuckDB analytical query engine for FedLens."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import duckdb

from fedlens.storage.paths import duckdb_path, gold_dir, silver_dir


def _register_parquets(conn: duckdb.DuckDBPyConnection) -> None:
    """Register all parquet files as DuckDB views."""
    # Silver layer
    for sub in ("parsed", "metadata"):
        d = silver_dir(sub)
        if d.exists():
            for pq in d.glob("*.parquet"):
                view_name = f"silver_{sub}_{pq.stem}"
                conn.execute(
                    f"CREATE OR REPLACE VIEW {view_name} AS "
                    f"SELECT * FROM read_parquet('{pq.as_posix()}')"
                )

    # Gold layer
    for sub in ("sentiment", "event_study", "topics", "drift", "embeddings"):
        d = gold_dir(sub)
        if d.exists():
            for pq in d.glob("*.parquet"):
                view_name = f"gold_{sub}_{pq.stem}"
                conn.execute(
                    f"CREATE OR REPLACE VIEW {view_name} AS "
                    f"SELECT * FROM read_parquet('{pq.as_posix()}')"
                )


@contextmanager
def get_connection() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """Get a DuckDB connection with all parquet views registered."""
    db = duckdb_path()
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(db))
    try:
        _register_parquets(conn)
        yield conn
    finally:
        conn.close()


def query(sql: str) -> list[dict]:
    """Run a SQL query and return results as list of dicts."""
    with get_connection() as conn:
        result = conn.execute(sql)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]
