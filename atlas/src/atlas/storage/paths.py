"""Canonical data directory layout for the bronze/silver/gold lake."""

from __future__ import annotations

from pathlib import Path

from atlas.config import get_settings


def data_root() -> Path:
    return Path(get_settings().data_dir).resolve()


def bronze_dir(source: str | None = None) -> Path:
    base = data_root() / "bronze"
    return base / source if source else base


def silver_dir(sub: str | None = None) -> Path:
    base = data_root() / "silver"
    return base / sub if sub else base


def gold_dir(sub: str | None = None) -> Path:
    base = data_root() / "gold"
    return base / sub if sub else base


def duckdb_path() -> Path:
    return data_root() / "atlas.duckdb"


def copilot_log_path() -> Path:
    return data_root() / "copilot_log.jsonl"


def ensure_dirs() -> None:
    """Create all data directories if they don't exist."""
    for source in ("fred", "yfinance"):
        bronze_dir(source).mkdir(parents=True, exist_ok=True)
    for sub in ("aligned", "transformed"):
        silver_dir(sub).mkdir(parents=True, exist_ok=True)
    for sub in ("features", "regime", "exports"):
        gold_dir(sub).mkdir(parents=True, exist_ok=True)
