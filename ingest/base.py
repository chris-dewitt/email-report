"""Base ingestor class for all data sources."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from .utils import sanitize_filename


class BaseIngestor(ABC):
    """Base class for data source ingestors."""

    def __init__(self, name: str, output_dir: Path, config: dict):
        self.name = name
        self.output_dir = output_dir / name
        self.config = config
        self.logger = logging.getLogger(f"ingest.{name}")

    @abstractmethod
    def fetch(self, series_cfg: dict) -> pd.DataFrame:
        """Fetch a single series. Returns a DataFrame with a datetime index."""
        ...

    def save(self, df: pd.DataFrame, series_id: str) -> Path:
        """Save a DataFrame as a Parquet file."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        filename = sanitize_filename(series_id) + ".parquet"
        path = self.output_dir / filename
        df.to_parquet(path)
        self.logger.info("Saved %s (%d rows)", path, len(df))
        return path

    def run(self) -> dict:
        """Fetch and save all series defined in config."""
        series_list = self.config.get("series", [])
        if not series_list:
            self.logger.warning("No series configured for %s", self.name)
            return {"ok": [], "failed": []}

        ok, failed = [], []

        for series_cfg in series_list:
            series_id = series_cfg["id"]
            try:
                self.logger.info("Fetching %s/%s ...", self.name, series_id)
                df = self.fetch(series_cfg)
                if df is not None and not df.empty:
                    self.save(df, series_id)
                    ok.append(series_id)
                else:
                    self.logger.warning("No data returned for %s", series_id)
                    failed.append(series_id)
            except Exception:
                self.logger.exception("Failed to fetch %s", series_id)
                failed.append(series_id)

        self.logger.info("%s complete: %d ok, %d failed", self.name, len(ok), len(failed))
        return {"ok": ok, "failed": failed}
