"""Rules-based macro regime classification.

Regimes:
    - Expansion: labor tight, growth positive, inflation moderate
    - Overheating: labor tight, inflation elevated, rates rising
    - Slowdown: growth decelerating, labor softening, claims rising
    - Contraction: growth negative, unemployment rising, claims elevated
    - Financial Stress: NFCI > 0, VIX elevated, credit spreads widening

Output: { regime, confidence, drivers[], as_of }
"""

from __future__ import annotations

from datetime import date

import polars as pl

from atlas.storage.parquet_store import read_gold, write_gold


def _get_latest_zscore(theme: str, series_id: str) -> float | None:
    """Read the latest z-score for a series from gold features."""
    df = read_gold(theme, sub="features")
    if df is None or df.is_empty():
        return None

    subset = df.filter(pl.col("series_id") == series_id)
    if subset.is_empty() or "value_zscore" not in subset.columns:
        return None

    # Get the last non-null z-score
    last = subset.filter(pl.col("value_zscore").is_not_null()).sort("date").tail(1)
    if last.is_empty():
        return None
    return last["value_zscore"][0]


def _get_latest_value(theme: str, series_id: str) -> float | None:
    """Read the latest value for a series from gold features."""
    df = read_gold(theme, sub="features")
    if df is None or df.is_empty():
        return None

    subset = df.filter(pl.col("series_id") == series_id)
    if subset.is_empty():
        return None

    last = subset.filter(pl.col("value").is_not_null()).sort("date").tail(1)
    if last.is_empty():
        return None
    return last["value"][0]


def compute_regime_snapshot() -> dict | None:
    """Compute the current macro regime based on latest feature z-scores.

    Returns dict: { regime, confidence, drivers, as_of } or None if no data.
    """
    # Gather key z-scores
    signals: dict[str, float | None] = {
        "unemployment_z": _get_latest_zscore("labor", "UNRATE"),
        "claims_z": _get_latest_zscore("labor", "ICSA"),
        "payrolls_z": _get_latest_zscore("labor", "PAYEMS"),
        "cpi_z": _get_latest_zscore("inflation", "CPIAUCSL"),
        "breakeven_z": _get_latest_zscore("inflation", "T5YIE"),
        "vix_z": _get_latest_zscore("fincond", "VIXCLS"),
        "hy_oas_z": _get_latest_zscore("fincond", "BAMLH0A0HYM2"),
        "nfci_val": _get_latest_value("fincond", "NFCI"),
        "ism_z": _get_latest_zscore("growth", "NAPM"),
        "indpro_z": _get_latest_zscore("growth", "INDPRO"),
        "t10y2y_z": _get_latest_zscore("rates", "T10Y2Y"),
    }

    # Check if we have enough data
    valid = {k: v for k, v in signals.items() if v is not None}
    if len(valid) < 5:
        return None

    # Default unknown to 0
    def s(key: str) -> float:
        return signals.get(key) or 0.0

    # ── Score each regime ────────────────────────────────────────────────
    scores: dict[str, float] = {}
    drivers_by_regime: dict[str, list[str]] = {}

    # Financial Stress (check first — overrides others)
    stress_score = 0.0
    stress_drivers: list[str] = []
    if s("vix_z") > 1.5:
        stress_score += 0.3
        stress_drivers.append(f"VIX z={s('vix_z'):.2f}")
    if s("hy_oas_z") > 1.0:
        stress_score += 0.3
        stress_drivers.append(f"HY OAS z={s('hy_oas_z'):.2f}")
    if (signals.get("nfci_val") or -1) > 0:
        stress_score += 0.4
        stress_drivers.append(f"NFCI={s('nfci_val'):.2f}")
    scores["financial_stress"] = stress_score
    drivers_by_regime["financial_stress"] = stress_drivers

    # Contraction
    contract_score = 0.0
    contract_drivers: list[str] = []
    if s("ism_z") < -0.5:
        contract_score += 0.3
        contract_drivers.append(f"ISM z={s('ism_z'):.2f}")
    if s("unemployment_z") > 0.5:
        contract_score += 0.3
        contract_drivers.append(f"Unemployment z={s('unemployment_z'):.2f}")
    if s("claims_z") > 1.0:
        contract_score += 0.2
        contract_drivers.append(f"Claims z={s('claims_z'):.2f}")
    if s("indpro_z") < -0.5:
        contract_score += 0.2
        contract_drivers.append(f"IndPro z={s('indpro_z'):.2f}")
    scores["contraction"] = contract_score
    drivers_by_regime["contraction"] = contract_drivers

    # Slowdown
    slow_score = 0.0
    slow_drivers: list[str] = []
    if -0.5 <= s("ism_z") < 0:
        slow_score += 0.3
        slow_drivers.append(f"ISM z={s('ism_z'):.2f}")
    if 0 < s("claims_z") <= 1.0:
        slow_score += 0.3
        slow_drivers.append(f"Claims z={s('claims_z'):.2f}")
    if s("payrolls_z") < 0:
        slow_score += 0.2
        slow_drivers.append(f"Payrolls z={s('payrolls_z'):.2f}")
    if s("t10y2y_z") < -0.5:
        slow_score += 0.2
        slow_drivers.append(f"Curve z={s('t10y2y_z'):.2f}")
    scores["slowdown"] = slow_score
    drivers_by_regime["slowdown"] = slow_drivers

    # Overheating
    hot_score = 0.0
    hot_drivers: list[str] = []
    if s("cpi_z") > 1.0:
        hot_score += 0.3
        hot_drivers.append(f"CPI z={s('cpi_z'):.2f}")
    if s("breakeven_z") > 0.5:
        hot_score += 0.2
        hot_drivers.append(f"Breakeven z={s('breakeven_z'):.2f}")
    if s("unemployment_z") < -0.5:
        hot_score += 0.3
        hot_drivers.append(f"Unemployment z={s('unemployment_z'):.2f} (tight)")
    if s("payrolls_z") > 0.5:
        hot_score += 0.2
        hot_drivers.append(f"Payrolls z={s('payrolls_z'):.2f}")
    scores["overheating"] = hot_score
    drivers_by_regime["overheating"] = hot_drivers

    # Expansion (default / healthy)
    expand_score = 0.0
    expand_drivers: list[str] = []
    if s("ism_z") >= 0:
        expand_score += 0.25
        expand_drivers.append(f"ISM z={s('ism_z'):.2f}")
    if s("unemployment_z") <= 0:
        expand_score += 0.25
        expand_drivers.append(f"Unemployment z={s('unemployment_z'):.2f}")
    if s("claims_z") <= 0:
        expand_score += 0.25
        expand_drivers.append(f"Claims z={s('claims_z'):.2f}")
    if abs(s("cpi_z")) < 1.0:
        expand_score += 0.25
        expand_drivers.append(f"CPI z={s('cpi_z'):.2f} (moderate)")
    scores["expansion"] = expand_score
    drivers_by_regime["expansion"] = expand_drivers

    # ── Pick the winner ──────────────────────────────────────────────────
    regime = max(scores, key=lambda k: scores[k])
    confidence = scores[regime]

    result = {
        "regime": regime,
        "confidence": min(confidence, 1.0),
        "drivers": drivers_by_regime[regime],
        "as_of": date.today().isoformat(),
        "all_scores": scores,
    }

    # Write to gold/regime
    snapshot_df = pl.DataFrame({
        "date": [date.today()],
        "regime": [regime],
        "confidence": [confidence],
        "drivers": [", ".join(drivers_by_regime[regime])],
    })
    write_gold(snapshot_df, "snapshot", sub="regime")

    return result
