"""Ingestion orchestrator — runs connectors and writes bronze parquets."""

from __future__ import annotations

from datetime import date

import polars as pl
from rich.console import Console
from rich.table import Table

from atlas.ingest.base import BaseConnector
from atlas.ingest.fred import FredConnector
from atlas.ingest.yfinance_conn import YFinanceConnector
from atlas.ingest.registry import (
    SERIES_CATALOG,
    SeriesDef,
    Source,
    get_series_by_source,
)
from atlas.storage.parquet_store import write_bronze
from atlas.config import get_settings

console = Console()


def _get_connectors() -> dict[Source, BaseConnector]:
    """Instantiate all available connectors."""
    connectors: dict[Source, BaseConnector] = {}

    try:
        connectors[Source.FRED] = FredConnector()
    except ValueError as e:
        console.print(f"[yellow]FRED connector unavailable: {e}[/yellow]")

    connectors[Source.YFINANCE] = YFinanceConnector()

    return connectors


def run_ingest(
    source_filter: Source | None = None,
    series_filter: str | None = None,
    start: date | None = None,
) -> dict[str, str]:
    """Run the full ingestion pipeline.

    Args:
        source_filter: Only pull from this source (None = all).
        series_filter: Only pull this series_id (None = all).
        start: History start date.

    Returns:
        Dict mapping series_id -> "ok" | error message.
    """
    settings = get_settings()
    if start is None:
        start = date.fromisoformat(settings.features.history_start)

    connectors = _get_connectors()
    results: dict[str, str] = {}

    # Determine which series to pull
    if series_filter:
        series_list = [s for s in SERIES_CATALOG if s.series_id == series_filter]
        if not series_list:
            console.print(f"[red]Series '{series_filter}' not found in catalog.[/red]")
            return {}
    elif source_filter:
        series_list = get_series_by_source(source_filter)
    else:
        series_list = list(SERIES_CATALOG)

    # Group by source and pull
    for sd in series_list:
        connector = connectors.get(sd.source)
        if connector is None:
            results[sd.series_id] = f"no connector for {sd.source.value}"
            continue

        try:
            df = connector.pull(sd, start=start)
            if df.is_empty():
                results[sd.series_id] = "empty response"
                continue

            path = write_bronze(df, sd.series_id, sd.source.value)
            results[sd.series_id] = f"ok ({len(df)} rows)"
        except Exception as e:
            results[sd.series_id] = f"error: {e}"

    return results


def print_ingest_report(results: dict[str, str]) -> None:
    """Pretty-print ingestion results."""
    table = Table(title="Atlas Ingestion Report")
    table.add_column("Series", style="cyan")
    table.add_column("Status", style="green")

    ok_count = 0
    for series_id, status in sorted(results.items()):
        style = "green" if status.startswith("ok") else "red"
        table.add_row(series_id, f"[{style}]{status}[/{style}]")
        if status.startswith("ok"):
            ok_count += 1

    console.print(table)
    console.print(
        f"\n[bold]{ok_count}/{len(results)} series pulled successfully.[/bold]"
    )
