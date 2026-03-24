"""Load and validate pipeline configuration."""

import os
import re
from pathlib import Path

import yaml


def _resolve_env_vars(value):
    """Replace ${ENV_VAR} patterns with environment variable values."""
    if isinstance(value, str):
        pattern = re.compile(r"\$\{(\w+)\}")
        def replacer(match):
            return os.environ.get(match.group(1), "")
        return pattern.sub(replacer, value)
    if isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_vars(item) for item in value]
    return value


def load_config(path: str | Path = "config.yaml") -> dict:
    """Load config from YAML file, resolving environment variables."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path) as f:
        raw = yaml.safe_load(f)

    config = _resolve_env_vars(raw)

    if "output_dir" not in config:
        config["output_dir"] = "./data"

    return config
