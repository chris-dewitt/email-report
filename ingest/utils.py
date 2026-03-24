"""Shared utilities for data ingestion."""

import logging
import re
import time

import requests

logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """Make a string safe for use as a filename."""
    return re.sub(r'[^\w\-.]', '_', name).strip('_')


def fetch_json(url: str, method: str = "GET", retries: int = 3, **kwargs) -> dict:
    """Fetch JSON from a URL with retry logic.

    Args:
        url: The URL to fetch.
        method: HTTP method (GET or POST).
        retries: Number of attempts.
        **kwargs: Passed to requests.request().

    Returns:
        Parsed JSON response.
    """
    kwargs.setdefault("timeout", 30)
    last_error = None

    for attempt in range(retries):
        try:
            resp = requests.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            last_error = e
            if attempt < retries - 1:
                wait = 2 ** attempt
                logger.warning("Attempt %d failed for %s: %s. Retrying in %ds...",
                               attempt + 1, url, e, wait)
                time.sleep(wait)

    raise last_error
