"""Persist scenario results as parquet files for analytical querying."""

from __future__ import annotations

from pathlib import Path

import polars as pl

from balancelab.config import GOLD_DIR
from balancelab.models.results import ScenarioOutput


def write_results(outputs: list[ScenarioOutput], path: Path | None = None) -> Path:
    target = path or (GOLD_DIR / "scenario_results.parquet")
    target.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for o in outputs:
        rows.append({
            "scenario_id": o.scenario_id,
            "scenario_name": o.scenario_name,
            "base_nii": o.nii.base_nii,
            "shocked_nii": o.nii.shocked_nii,
            "delta_nii": o.nii.delta_nii,
            "delta_nii_pct": o.nii.delta_nii_pct,
            "base_eve": o.eve.base_eve,
            "shocked_eve": o.eve.shocked_eve,
            "delta_eve": o.eve.delta_eve,
            "delta_eve_pct": o.eve.delta_eve_pct,
            "asset_duration": o.eve.asset_duration,
            "liability_duration": o.eve.liability_duration,
            "duration_gap": o.eve.duration_gap,
            "net_gap": o.liquidity.net_gap,
            "one_year_cumulative_gap": o.liquidity.one_year_cumulative_gap,
        })

    df = pl.DataFrame(rows)
    df.write_parquet(target)
    return target


def read_results(path: Path | None = None) -> pl.DataFrame:
    target = path or (GOLD_DIR / "scenario_results.parquet")
    if not target.exists():
        return pl.DataFrame()
    return pl.read_parquet(target)
