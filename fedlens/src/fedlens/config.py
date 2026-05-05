"""YAML + env config loader for FedLens."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

from fedlens.settings import FedLensSettings

load_dotenv()

_SEARCH_NAMES = ("fedlens.yaml", "fedlens.yml")


def _find_config_file() -> Path | None:
    """Walk up from CWD looking for fedlens.yaml."""
    cwd = Path.cwd()
    for directory in [cwd, *cwd.parents]:
        for name in _SEARCH_NAMES:
            candidate = directory / name
            if candidate.exists():
                return candidate
    return None


def _load_yaml_overrides() -> dict:
    path = _find_config_file()
    if path is None:
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def get_settings() -> FedLensSettings:
    """Build settings from YAML config + env vars."""
    overrides = _load_yaml_overrides()
    return FedLensSettings(**overrides)
