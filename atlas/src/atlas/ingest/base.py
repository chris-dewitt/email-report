"""Base connector ABC for all data source connectors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

import polars as pl

from atlas.ingest.registry import SeriesDef


class BaseConnector(ABC):
    """Abstract base class for data source connectors.

    Each connector pulls raw data for a list of series and returns
    a polars DataFrame with columns: date (Date), value (Float64).
    """

    @abstractmethod
    def pull(self, series_def: SeriesDef, start: date | None = None) -> pl.DataFrame:
        """Pull a single series from the source.

        Returns:
            DataFrame with columns [date: Date, value: Float64]
        """
        ...

    @abstractmethod
    def supports(self, series_def: SeriesDef) -> bool:
        """Whether this connector can handle the given series."""
        ...

    def pull_many(
        self,
        series_defs: list[SeriesDef],
        start: date | None = None,
    ) -> dict[str, pl.DataFrame | Exception]:
        """Pull multiple series, collecting results and errors.

        Returns:
            Dict mapping series_id -> DataFrame or Exception.
        """
        results: dict[str, pl.DataFrame | Exception] = {}
        for sd in series_defs:
            if not self.supports(sd):
                results[sd.series_id] = ValueError(f"Unsupported series: {sd.series_id}")
                continue
            try:
                df = self.pull(sd, start=start)
                results[sd.series_id] = df
            except Exception as e:
                results[sd.series_id] = e
        return results
