"""Shared test fixtures for FedLens."""

from __future__ import annotations

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def tmp_data_dir(tmp_path):
    """Provide a temporary data directory for tests."""
    for sub in (
        "bronze/statements",
        "bronze/minutes",
        "bronze/speeches",
        "bronze/pressconf",
        "silver/parsed",
        "silver/metadata",
        "gold/embeddings",
        "gold/sentiment",
        "gold/event_study",
        "gold/topics",
        "gold/drift",
        "vector",
        "reviews",
    ):
        (tmp_path / sub).mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def sample_statement_html():
    """Sample FOMC statement HTML for testing."""
    return """
    <div class="col-xs-12 col-sm-8 col-md-8">
        <h3 class="title">Federal Reserve issues FOMC statement</h3>
        <p class="article__time"><time datetime="2024-01-31">January 31, 2024</time></p>
        <div class="col-xs-12 col-sm-8 col-md-8">
            <p>Recent indicators suggest that economic activity has been expanding at a solid pace.
            Job gains have moderated since early last year but remain strong, and the unemployment
            rate has remained low. Inflation has eased over the past year but remains elevated.
            The Committee seeks to achieve maximum employment and inflation at the rate of 2 percent
            over the longer run.</p>
            <p>The Committee decided to maintain the target range for the federal funds rate at
            5-1/4 to 5-1/2 percent. The Committee does not expect it will be appropriate to reduce
            the target range until it has gained greater confidence that inflation is moving
            sustainably toward 2 percent.</p>
        </div>
    </div>
    """
