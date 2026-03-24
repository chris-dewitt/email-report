"""OECD data ingestor via SDMX JSON API."""

from pathlib import Path

import pandas as pd

from ..base import BaseIngestor
from ..utils import fetch_json


class OecdIngestor(BaseIngestor):

    BASE_URL = "https://stats.oecd.org/SDMX-JSON/data"

    def __init__(self, output_dir: Path, config: dict):
        super().__init__("oecd", output_dir, config)

    def fetch(self, series_cfg: dict) -> pd.DataFrame:
        dataset = series_cfg.get("dataset", "")
        dimension_path = series_cfg["id"]

        url = f"{self.BASE_URL}/{dataset}/{dimension_path}/all"
        params = {"dimensionAtObservation": "allDimensions"}

        data = fetch_json(url, params=params)
        return self._parse_sdmx_json(data)

    def _parse_sdmx_json(self, data: dict) -> pd.DataFrame:
        """Parse OECD SDMX-JSON response into a DataFrame."""
        try:
            datasets = data["dataSets"]
            if not datasets:
                return pd.DataFrame()

            observations = datasets[0].get("observations", {})
            if not observations:
                # Try series-level structure
                series_data = datasets[0].get("series", {})
                if not series_data:
                    return pd.DataFrame()
                return self._parse_series_structure(data, series_data)

            # Flat observation structure
            time_dim = data["structure"]["dimensions"]["observation"]
            time_idx = None
            for i, dim in enumerate(time_dim):
                if dim["id"] in ("TIME_PERIOD", "TIME"):
                    time_idx = i
                    time_values = dim["values"]
                    break

            if time_idx is None:
                self.logger.warning("No time dimension found in OECD response")
                return pd.DataFrame()

            rows = []
            for key, obs in observations.items():
                indices = key.split(":")
                time_pos = int(indices[time_idx])
                period = time_values[time_pos]["id"]
                value = obs[0] if obs else None
                rows.append({"date": period, "value": value})

            df = pd.DataFrame(rows)
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").sort_index().dropna()
            return df

        except (KeyError, IndexError) as e:
            self.logger.error("Failed to parse OECD response: %s", e)
            return pd.DataFrame()

    def _parse_series_structure(self, data: dict, series_data: dict) -> pd.DataFrame:
        """Parse series-level SDMX-JSON structure."""
        time_dim = data["structure"]["dimensions"]["observation"]
        time_values = None
        for dim in time_dim:
            if dim["id"] in ("TIME_PERIOD", "TIME"):
                time_values = dim["values"]
                break

        if time_values is None:
            return pd.DataFrame()

        rows = []
        for _series_key, series_obj in series_data.items():
            observations = series_obj.get("observations", {})
            for time_pos_str, obs in observations.items():
                time_pos = int(time_pos_str)
                period = time_values[time_pos]["id"]
                value = obs[0] if obs else None
                rows.append({"date": period, "value": value})

        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index().dropna()
        return df
