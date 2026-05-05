"""Feature pipeline: bronze → silver → gold.

Orchestrates calendar alignment, transforms, and themed feature block creation.
"""

from __future__ import annotations

from rich.console import Console

import polars as pl

from atlas.ingest.registry import (
    SERIES_CATALOG,
    SERIES_MAP,
    Frequency,
    Theme,
    get_series_by_theme,
)
from atlas.features.calendar import align_all_series
from atlas.features.transforms import z_score, yoy_change, rolling_change, log_diff, level_diff
from atlas.storage.parquet_store import (
    read_bronze,
    write_silver,
    write_gold,
    read_silver,
)

console = Console()


def _load_bronze_series() -> dict[str, tuple[pl.DataFrame, Frequency]]:
    """Load all available bronze series."""
    result: dict[str, tuple[pl.DataFrame, Frequency]] = {}
    for sd in SERIES_CATALOG:
        df = read_bronze(sd.series_id, sd.source.value)
        if df is not None and not df.is_empty():
            # Keep only date and value columns
            df = df.select("date", "value").sort("date")
            result[sd.series_id] = (df, sd.frequency)
    return result


def _build_silver(bronze: dict[str, tuple[pl.DataFrame, Frequency]]) -> dict[str, pl.DataFrame]:
    """Bronze → Silver: align to business-day calendar."""
    console.print("  [cyan]Aligning to business-day calendar...[/cyan]")
    aligned = align_all_series(bronze)

    # Write silver aligned parquets
    for sid, df in aligned.items():
        write_silver(df.with_columns(pl.lit(sid).alias("series_id")), sid, sub="aligned")

    console.print(f"  [green][OK] {len(aligned)} series aligned.[/green]")
    return aligned


def _apply_transforms(
    aligned: dict[str, pl.DataFrame],
) -> dict[str, pl.DataFrame]:
    """Silver aligned → Silver transformed: apply rolling stats."""
    console.print("  [cyan]Applying transforms...[/cyan]")

    transformed: dict[str, pl.DataFrame] = {}
    for sid, df in aligned.items():
        sd = SERIES_MAP.get(sid)
        if sd is None:
            continue

        t = df.clone()

        # Apply transforms based on frequency
        if sd.frequency == Frequency.DAILY:
            t = z_score(t, window=504)
            t = rolling_change(t, window=5)   # 1-week change
            t = rolling_change(t, window=21)  # 1-month change
            t = log_diff(t)
        elif sd.frequency == Frequency.WEEKLY:
            t = z_score(t, window=104)  # ~2 years of weeks
            t = rolling_change(t, window=4)   # 1-month change
        elif sd.frequency == Frequency.MONTHLY:
            t = z_score(t, window=24)   # 2 years of months (but on bday calendar)
            t = yoy_change(t, periods=252)   # ~12 months of bdays
            t = level_diff(t)
        elif sd.frequency == Frequency.QUARTERLY:
            t = z_score(t, window=8)
            t = yoy_change(t, periods=252)

        transformed[sid] = t
        write_silver(t.with_columns(pl.lit(sid).alias("series_id")), sid, sub="transformed")

    console.print(f"  [green][OK] {len(transformed)} series transformed.[/green]")
    return transformed


def _build_gold_features(
    transformed: dict[str, pl.DataFrame],
    theme_filter: str | None = None,
) -> int:
    """Silver transformed → Gold: build themed feature blocks."""
    console.print("  [cyan]Building themed feature blocks...[/cyan]")

    total_rows = 0
    themes = [Theme(theme_filter)] if theme_filter else list(Theme)

    for theme in themes:
        theme_series = get_series_by_theme(theme)
        theme_dfs: list[pl.DataFrame] = []

        for sd in theme_series:
            t = transformed.get(sd.series_id)
            if t is None:
                continue

            # Select date + value + all computed columns, add series_id
            cols = [c for c in t.columns if c != "series_id"]
            subset = t.select(cols).with_columns(pl.lit(sd.series_id).alias("series_id"))
            theme_dfs.append(subset)

        if theme_dfs:
            # Stack all series in this theme (long format)
            combined = pl.concat(theme_dfs, how="diagonal_relaxed")
            write_gold(combined, theme.value, sub="features")
            total_rows += len(combined)
            console.print(f"    [green][OK] {theme.value}: {len(combined):,} rows[/green]")

    return total_rows


def run_feature_pipeline(theme_filter: str | None = None) -> dict[str, int]:
    """Execute the full feature pipeline: bronze → silver → gold.

    Returns:
        Dict with layer names and row counts.
    """
    stats: dict[str, int] = {}

    # Load bronze
    bronze = _load_bronze_series()
    stats["bronze_series"] = len(bronze)

    if not bronze:
        console.print("[red]No bronze data found. Run 'atlas pull' first.[/red]")
        return stats

    # Bronze → Silver (aligned)
    aligned = _build_silver(bronze)
    stats["silver_aligned"] = sum(len(df) for df in aligned.values())

    # Silver aligned → Silver transformed
    transformed = _apply_transforms(aligned)
    stats["silver_transformed"] = sum(len(df) for df in transformed.values())

    # Silver transformed → Gold features
    gold_rows = _build_gold_features(transformed, theme_filter)
    stats["gold_features"] = gold_rows

    return stats
