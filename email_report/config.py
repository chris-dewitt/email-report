"""Load email report configuration."""

import sys
from pathlib import Path

# Add project root so we can reuse ingest utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingest.config import _resolve_env_vars

import yaml


def load_email_config(path: str | Path = "email_config.yaml") -> dict:
    """Load email config from YAML, resolving environment variables."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path) as f:
        raw = yaml.safe_load(f)

    return _resolve_env_vars(raw)
