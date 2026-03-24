"""Yahoo Finance ingestor."""

from pathlib import Path

import pandas as pd
import yfinance as yf

from ..base import BaseIngestor


class YFinanceIngestor(BaseIngestor):

    def __init__(self, output_dir: Path, config: dict):
        super().__init__("yfinance", output_dir, config)

    def fetch(self, series_cfg: dict) -> pd.DataFrame:
        ticker = series_cfg["id"]
        period = series_cfg.get("period", "5y")
        interval = series_cfg.get("interval", "1d")

        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True,
        )

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

        df.index.name = "date"
        return df
