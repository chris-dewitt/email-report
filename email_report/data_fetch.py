"""Fetch interest rates, yield curve, and Fed Funds futures data."""

import logging
import time
from datetime import datetime, timedelta

import pandas as pd
from fredapi import Fred
import yfinance as yf

logger = logging.getLogger(__name__)

# CME month codes for Fed Funds futures
MONTH_CODES = {
    1: "F", 2: "G", 3: "H", 4: "J", 5: "K", 6: "M",
    7: "N", 8: "Q", 9: "U", 10: "V", 11: "X", 12: "Z",
}

MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


def fetch_rates(fred: Fred, series_list: list[dict]) -> pd.DataFrame:
    """Fetch current level and daily change for each rate series.

    Returns DataFrame with columns: label, category, current, previous, change.
    """
    rows = []
    for entry in series_list:
        series_id = entry["id"]
        try:
            data = fred.get_series(series_id).dropna()
            if len(data) < 2:
                logger.warning("Not enough data for %s", series_id)
                continue
            current = float(data.iloc[-1])
            previous = float(data.iloc[-2])
            rows.append({
                "label": entry["label"],
                "category": entry["category"],
                "current": current,
                "previous": previous,
                "change": current - previous,
            })
        except Exception:
            logger.exception("Failed to fetch rate %s", series_id)
        time.sleep(0.1)

    return pd.DataFrame(rows)


def fetch_yield_curve(fred: Fred, curve_config: list[dict]) -> dict:
    """Fetch today and yesterday values for each tenor on the yield curve.

    Returns {"today": {tenor: rate}, "yesterday": {tenor: rate}}.
    """
    today = {}
    yesterday = {}
    for entry in curve_config:
        series_id = entry["id"]
        tenor = entry["tenor"]
        try:
            data = fred.get_series(series_id).dropna()
            if len(data) >= 1:
                today[tenor] = float(data.iloc[-1])
            if len(data) >= 2:
                yesterday[tenor] = float(data.iloc[-2])
        except Exception:
            logger.exception("Failed to fetch yield curve point %s", series_id)
        time.sleep(0.1)

    return {"today": today, "yesterday": yesterday}


def _generate_ff_tickers(n_months: int = 12) -> list[tuple[str, str]]:
    """Generate Fed Funds futures tickers for the next n months.

    Returns list of (ticker, display_label) tuples.
    """
    now = datetime.now()
    tickers = []
    for i in range(n_months):
        month = (now.month + i - 1) % 12 + 1
        year = now.year + (now.month + i - 1) // 12
        code = MONTH_CODES[month]
        yr2 = year % 100
        ticker = f"ZQ{code}{yr2:02d}.CBT"
        label = f"{MONTH_NAMES[month]} {year}"
        tickers.append((ticker, label))
    return tickers


def fetch_fed_funds_futures(n_months: int = 12) -> dict:
    """Fetch implied Fed Funds rates from CME futures via yfinance.

    Returns {"today": {label: rate}, "yesterday": {label: rate}}.
    """
    tickers_info = _generate_ff_tickers(n_months)
    ticker_strs = [t[0] for t in tickers_info]

    today = {}
    yesterday = {}

    try:
        data = yf.download(
            ticker_strs,
            period="5d",
            interval="1d",
            progress=False,
            group_by="ticker",
        )

        for ticker, label in tickers_info:
            try:
                if len(ticker_strs) == 1:
                    closes = data["Close"].dropna()
                else:
                    closes = data[ticker]["Close"].dropna()

                if len(closes) >= 1:
                    today[label] = round(100.0 - float(closes.iloc[-1]), 4)
                if len(closes) >= 2:
                    yesterday[label] = round(100.0 - float(closes.iloc[-2]), 4)
            except (KeyError, IndexError):
                logger.warning("No data for futures contract %s", ticker)
    except Exception:
        logger.exception("Failed to download Fed Funds futures")

    return {"today": today, "yesterday": yesterday}


def fetch_all(config: dict) -> dict:
    """Fetch all data sections. Returns dict with results and any errors."""
    errors = []
    result = {
        "rates_df": pd.DataFrame(),
        "yield_curve": {"today": {}, "yesterday": {}},
        "fed_futures": {"today": {}, "yesterday": {}},
        "errors": errors,
    }

    api_key = config.get("fred", {}).get("api_key", "")
    if not api_key:
        errors.append("FRED_API_KEY not set — rate and yield curve data unavailable")
        logger.error("FRED_API_KEY is not configured")
    else:
        fred = Fred(api_key=api_key)

        try:
            result["rates_df"] = fetch_rates(fred, config.get("rates", []))
        except Exception:
            logger.exception("Failed to fetch rates")
            errors.append("Failed to fetch interest rates")

        try:
            result["yield_curve"] = fetch_yield_curve(fred, config.get("yield_curve", []))
        except Exception:
            logger.exception("Failed to fetch yield curve")
            errors.append("Failed to fetch yield curve data")

    ff_config = config.get("fed_funds_futures", {})
    if ff_config.get("enabled", False):
        try:
            result["fed_futures"] = fetch_fed_funds_futures(
                n_months=ff_config.get("n_months", 12)
            )
        except Exception:
            logger.exception("Failed to fetch Fed Funds futures")
            errors.append("Failed to fetch Fed Funds futures")

    return result
