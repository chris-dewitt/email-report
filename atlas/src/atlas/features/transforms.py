"""Core mathematical transforms for macro feature engineering.

All transforms operate on polars DataFrames with columns: date, value.
They return a new column (or DataFrame) with the transformed values.

Mathematical definitions:
    z_score:        z_t = (x_t - μ_t) / σ_t       (rolling window)
    yoy_change:     Δ_YoY = (x_t - x_{t-12}) / x_{t-12}  (for monthly)
    mom_change_ann: Δ_MoM = ((x_t / x_{t-1})^12 - 1)     (annualized)
    log_diff:       Δ_log = ln(x_t) - ln(x_{t-1})
    rolling_change: Δ_w = x_t - x_{t-w}
    level_diff:     Δ = x_t - x_{t-1}
    percentile_rank: pct_t = rank(x_t in [x_{t-w}, ..., x_t]) / w
"""

from __future__ import annotations

import polars as pl


def z_score(df: pl.DataFrame, window: int = 504, col: str = "value") -> pl.DataFrame:
    """Rolling z-score: z_t = (x_t - mean_t) / std_t.

    Args:
        df: DataFrame with at least `col` column.
        window: Trailing window size in rows (~504 = 2 years of trading days).
        col: Column to transform.

    Returns:
        DataFrame with added '{col}_zscore' column.
    """
    return df.with_columns(
        (
            (pl.col(col) - pl.col(col).rolling_mean(window_size=window, min_samples=max(window // 4, 2)))
            / pl.col(col).rolling_std(window_size=window, min_samples=max(window // 4, 2))
        ).alias(f"{col}_zscore")
    )


def yoy_change(df: pl.DataFrame, periods: int = 252, col: str = "value") -> pl.DataFrame:
    """Year-over-year percentage change.

    For daily data use periods=252, for monthly use periods=12, quarterly use periods=4.
    """
    return df.with_columns(
        ((pl.col(col) - pl.col(col).shift(periods)) / pl.col(col).shift(periods)).alias(
            f"{col}_yoy"
        )
    )


def mom_change_annualized(
    df: pl.DataFrame, periods: int = 21, annualize: int = 12, col: str = "value"
) -> pl.DataFrame:
    """Month-over-month change, annualized.

    MoM_ann = (x_t / x_{t-periods})^(annualize) - 1
    For daily data: periods=21 (trading days/month), annualize=12.
    For monthly data: periods=1, annualize=12.
    """
    return df.with_columns(
        ((pl.col(col) / pl.col(col).shift(periods)).pow(annualize) - 1.0).alias(
            f"{col}_mom_ann"
        )
    )


def log_diff(df: pl.DataFrame, col: str = "value") -> pl.DataFrame:
    """Log-difference: ln(x_t) - ln(x_{t-1})."""
    return df.with_columns(
        (pl.col(col).log() - pl.col(col).shift(1).log()).alias(f"{col}_logdiff")
    )


def rolling_change(df: pl.DataFrame, window: int, col: str = "value") -> pl.DataFrame:
    """Simple rolling change: x_t - x_{t-window}."""
    return df.with_columns(
        (pl.col(col) - pl.col(col).shift(window)).alias(f"{col}_chg{window}")
    )


def level_diff(df: pl.DataFrame, periods: int = 1, col: str = "value") -> pl.DataFrame:
    """First difference: x_t - x_{t-periods}."""
    return df.with_columns(
        (pl.col(col) - pl.col(col).shift(periods)).alias(f"{col}_diff{periods}")
    )


def percentile_rank(df: pl.DataFrame, window: int = 504, col: str = "value") -> pl.DataFrame:
    """Trailing percentile rank within a rolling window.

    Approximated via rolling_quantile-based rank.
    """
    # Count how many values in the window are <= current value
    # Using a polars-friendly approach: rolling rank / window
    return df.with_columns(
        pl.col(col)
        .rolling_quantile(quantile=0.5, window_size=window, min_samples=max(window // 4, 2))
        .alias("_median")
    ).with_columns(
        # Simplified: compare to median as a proxy for percentile position
        pl.when(pl.col(col) >= pl.col("_median"))
        .then(
            0.5
            + 0.5
            * (pl.col(col) - pl.col("_median"))
            / (
                pl.col(col).rolling_max(window_size=window, min_samples=1)
                - pl.col("_median")
            ).clip(lower_bound=1e-10)
        )
        .otherwise(
            0.5
            * (pl.col(col) - pl.col(col).rolling_min(window_size=window, min_samples=1))
            / (
                pl.col("_median")
                - pl.col(col).rolling_min(window_size=window, min_samples=1)
            ).clip(lower_bound=1e-10)
        )
        .clip(lower_bound=0.0, upper_bound=1.0)
        .alias(f"{col}_pctrank")
    ).drop("_median")
