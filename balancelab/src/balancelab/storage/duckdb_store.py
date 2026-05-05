"""DuckDB analytical store for BalanceLab scenario results."""

from __future__ import annotations

import duckdb
import polars as pl

from balancelab.config import DUCKDB_PATH, GOLD_DIR


def get_connection() -> duckdb.DuckDBPyConnection:
    DUCKDB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DUCKDB_PATH))


def register_views(conn: duckdb.DuckDBPyConnection | None = None) -> None:
    conn = conn or get_connection()
    results_path = GOLD_DIR / "scenario_results.parquet"
    if results_path.exists():
        conn.execute(
            f"CREATE OR REPLACE VIEW scenario_results AS SELECT * FROM '{results_path}'"
        )


def query(sql: str, conn: duckdb.DuckDBPyConnection | None = None) -> pl.DataFrame:
    conn = conn or get_connection()
    register_views(conn)
    return conn.execute(sql).pl()
