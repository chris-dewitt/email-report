"""World Bank data ingestor via REST API."""

from pathlib import Path

import pandas as pd

from ..base import BaseIngestor
from ..utils import fetch_json


class WorldBankIngestor(BaseIngestor):

    BASE_URL = "https://api.worldbank.org/v2"

    def __init__(self, output_dir: Path, config: dict):
        super().__init__("worldbank", output_dir, config)

    def fetch(self, series_cfg: dict) -> pd.DataFrame:
        indicator = series_cfg["id"]
        country = series_cfg.get("country", "US")

        url = f"{self.BASE_URL}/country/{country}/indicator/{indicator}"
        params = {"format": "json", "per_page": 1000}

        data = fetch_json(url, params=params)

        # World Bank API returns [metadata, records]
        if not isinstance(data, list) or len(data) < 2:
            self.logger.warning("Unexpected response format for %s", indicator)
            return pd.DataFrame()

        records = data[1]
        if not records:
            return pd.DataFrame()

        rows = []
        for rec in records:
            if rec.get("value") is not None:
                rows.append({
                    "date": pd.Timestamp(year=int(rec["date"]), month=1, day=1),
                    "value": float(rec["value"]),
                })

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        df = df.set_index("date").sort_index()
        return df
