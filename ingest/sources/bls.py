"""Bureau of Labor Statistics (BLS) ingestor."""

from pathlib import Path

import pandas as pd

from ..base import BaseIngestor
from ..utils import fetch_json


class BlsIngestor(BaseIngestor):

    API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    def __init__(self, output_dir: Path, config: dict):
        super().__init__("bls", output_dir, config)
        self.api_key = config.get("api_key", "")
        self.start_year = config.get("start_year", "2015")
        self.end_year = config.get("end_year", "2026")

    def fetch(self, series_cfg: dict) -> pd.DataFrame:
        series_id = series_cfg["id"]

        payload = {
            "seriesid": [series_id],
            "startyear": self.start_year,
            "endyear": self.end_year,
        }
        if self.api_key:
            payload["registrationkey"] = self.api_key

        data = fetch_json(self.API_URL, method="POST", json=payload)

        if data.get("status") != "REQUEST_SUCCEEDED":
            msg = data.get("message", ["Unknown error"])
            self.logger.error("BLS API error for %s: %s", series_id, msg)
            return pd.DataFrame()

        results = data.get("Results", {}).get("series", [])
        if not results:
            return pd.DataFrame()

        return self._parse_series(results[0].get("data", []))

    def _parse_series(self, data: list[dict]) -> pd.DataFrame:
        """Parse BLS series data into a DataFrame."""
        rows = []
        for entry in data:
            year = entry["year"]
            period = entry["period"]

            # Skip annual averages (M13) and semi-annual (S01, S02)
            if not period.startswith("M") or period == "M13":
                continue

            month = int(period[1:])
            date = pd.Timestamp(year=int(year), month=month, day=1)
            value = float(entry["value"])
            rows.append({"date": date, "value": value})

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        df = df.set_index("date").sort_index()
        return df
