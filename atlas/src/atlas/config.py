"""Configuration loader — merges atlas.yaml + environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from atlas.settings import AtlasSettings, OllamaSettings, APISettings, FeatureSettings


def _find_config_file() -> Path | None:
    """Walk up from CWD looking for atlas.yaml."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / "atlas.yaml"
        if candidate.exists():
            return candidate
    return None


def _load_yaml_overrides() -> dict:
    """Load atlas.yaml if it exists."""
    config_path = _find_config_file()
    if config_path is None:
        return {}
    with open(config_path) as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def get_settings() -> AtlasSettings:
    """Build settings by merging YAML defaults with env var overrides."""
    yaml_data = _load_yaml_overrides()

    ollama_data = yaml_data.get("ollama", {})
    api_data = yaml_data.get("api", {})
    features_data = yaml_data.get("features", {})

    settings = AtlasSettings(
        data_dir=yaml_data.get("data_dir", "./data"),
        ollama=OllamaSettings(**ollama_data),
        api=APISettings(**api_data),
        features=FeatureSettings(**features_data),
    )
    return settings
