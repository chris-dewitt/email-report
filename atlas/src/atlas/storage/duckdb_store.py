"""DuckDB analytical query engine — registers parquet views and runs queries."""

from __future__ import annotations

from pathlib import Path

import duckdb
import polars as pl

from atlas.storage.paths import duckdb_path, bronze_dir, silver_dir, gold_dir


class DuckDBStore:
    """Thin wrapper around DuckDB for Atlas analytical queries."""

    def __init__(self, db_path: Path | None = None):
        self._path = db_path or duckdb_path()
        self._conn: duckdb.DuckDBPyConnection | None = None

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            self._conn = duckdb.connect(str(self._path))
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # ── View Registration ───────────────────────────────────────────────

    def register_views(self) -> dict[str, int]:
        """Register all parquet layers as DuckDB views. Returns view name → row count."""
        stats: dict[str, int] = {}

        # Bronze views
        for source_dir in bronze_dir().iterdir():
            if source_dir.is_dir():
                pattern = str(source_dir / "*.parquet").replace("\\", "/")
                files = list(source_dir.glob("*.parquet"))
                if files:
                    view_name = f"bronze_{source_dir.name}"
                    self.conn.execute(
                        f"CREATE OR REPLACE VIEW {view_name} AS "
                        f"SELECT * FROM read_parquet('{pattern}')"
                    )
                    count = self.conn.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
                    stats[view_name] = count[0] if count else 0

        # Silver views
        for sub in ("aligned", "transformed"):
            sub_dir = silver_dir(sub)
            files = list(sub_dir.glob("*.parquet"))
            if files:
                pattern = str(sub_dir / "*.parquet").replace("\\", "/")
                view_name = f"silver_{sub}"
                self.conn.execute(
                    f"CREATE OR REPLACE VIEW {view_name} AS "
                    f"SELECT * FROM read_parquet('{pattern}')"
                )
                count = self.conn.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
                stats[view_name] = count[0] if count else 0

        # Gold views
        for sub in ("features", "regime"):
            sub_dir = gold_dir(sub)
            files = list(sub_dir.glob("*.parquet"))
            if files:
                pattern = str(sub_dir / "*.parquet").replace("\\", "/")
                view_name = f"gold_{sub}"
                self.conn.execute(
                    f"CREATE OR REPLACE VIEW {view_name} AS "
                    f"SELECT * FROM read_parquet('{pattern}')"
                )
                count = self.conn.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
                stats[view_name] = count[0] if count else 0

        return stats

    # ── Query Helpers ───────────────────────────────────────────────────

    def query_df(self, sql: str) -> pl.DataFrame:
        """Execute SQL and return a polars DataFrame."""
        result = self.conn.execute(sql)
        return pl.from_arrow(result.fetch_arrow_table())

    def query_one(self, sql: str) -> tuple | None:
        """Execute SQL and return the first row as a tuple."""
        result = self.conn.execute(sql).fetchone()
        return result

    def table_stats(self) -> dict[str, int]:
        """Return row counts for all registered views."""
        views = self.conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_type = 'VIEW'"
        ).fetchall()
        return {v[0]: self.conn.execute(f"SELECT COUNT(*) FROM {v[0]}").fetchone()[0] for v in views}
