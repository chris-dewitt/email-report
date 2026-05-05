"""Typed settings loaded from environment variables and atlas.yaml."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class OllamaSettings(BaseSettings):
    host: str = "http://localhost:11434"
    model: str = "mistral"
    timeout_seconds: int = 120


class APISettings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


class FeatureSettings(BaseSettings):
    zscore_window: int = 504
    lookback_default_days: int = 7
    history_start: str = "2015-01-01"


class AtlasSettings(BaseSettings):
    """Root settings — merges env vars and atlas.yaml."""

    model_config = {"env_prefix": "ATLAS_", "env_file": ".env", "extra": "ignore"}

    fred_api_key: str = Field(default="", alias="FRED_API_KEY")
    data_dir: Path = Path("./data")

    ollama: OllamaSettings = OllamaSettings()
    api: APISettings = APISettings()
    features: FeatureSettings = FeatureSettings()
