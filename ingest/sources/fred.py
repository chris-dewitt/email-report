"""FRED (Federal Reserve Economic Data) ingestor."""

from pathlib import Path

import pandas as pd
from fredapi import Fred

from ..base import BaseIngestor


class FredIngestor(BaseIngestor):

    def __init__(self, output_dir: Path, config: dict):
        super().__init__("fred", output_dir, config)
        api_key = config.get("api_key", "")
        if not api_key:
            raise ValueError(
                "FRED_API_KEY is required. Get a free key at "
                "https://fred.stlouisfed.org/docs/api/api_key.html "
                "and set it as an environment variable."
            )
        self.client = Fred(api_key=api_key)

    def fetch(self, series_cfg: dict) -> pd.DataFrame:
        series_id = series_cfg["id"]
        data = self.client.get_series(series_id)
        df = data.to_frame(name="value")
        df.index.name = "date"
        df = df.dropna()
        return df
