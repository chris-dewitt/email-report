"""Tests for the series registry / catalog."""

from atlas.ingest.registry import (
    SERIES_CATALOG,
    SERIES_MAP,
    Source,
    Theme,
    get_series,
    get_series_by_source,
    get_series_by_theme,
)


def test_catalog_has_36_series():
    assert len(SERIES_CATALOG) == 36


def test_all_series_have_unique_ids():
    ids = [s.series_id for s in SERIES_CATALOG]
    assert len(ids) == len(set(ids))


def test_all_themes_represented():
    themes = {s.theme for s in SERIES_CATALOG}
    assert themes == set(Theme)


def test_fred_series_count():
    fred = get_series_by_source(Source.FRED)
    assert len(fred) == 32


def test_yfinance_series_count():
    yf = get_series_by_source(Source.YFINANCE)
    assert len(yf) == 4


def test_get_series_by_id():
    s = get_series("CPIAUCSL")
    assert s is not None
    assert s.theme == Theme.INFLATION
    assert s.source == Source.FRED


def test_get_series_unknown():
    assert get_series("FAKE_SERIES") is None


def test_inflation_theme_count():
    inf = get_series_by_theme(Theme.INFLATION)
    assert len(inf) == 7


def test_series_map_consistency():
    assert len(SERIES_MAP) == len(SERIES_CATALOG)
