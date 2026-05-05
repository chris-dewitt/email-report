"""Repricing gap and liquidity gap table construction."""

from __future__ import annotations

from balancelab.models.positions import BalanceSheet, RepricingBucket
from balancelab.models.results import GapTableRow, LiquidityGapResult

ORDERED_BUCKETS = [
    RepricingBucket.OVERNIGHT,
    RepricingBucket.M1,
    RepricingBucket.M3,
    RepricingBucket.M6,
    RepricingBucket.Y1,
    RepricingBucket.Y2,
    RepricingBucket.Y3,
    RepricingBucket.Y5,
    RepricingBucket.Y10,
    RepricingBucket.Y10_PLUS,
    RepricingBucket.NON_REPRICING,
]

ONE_YEAR_BUCKETS = {
    RepricingBucket.OVERNIGHT,
    RepricingBucket.M1,
    RepricingBucket.M3,
    RepricingBucket.M6,
    RepricingBucket.Y1,
}


def compute_liquidity_gap(bs: BalanceSheet) -> LiquidityGapResult:
    total_assets = bs.total_assets
    rows: list[GapTableRow] = []
    cumulative = 0.0
    total_rsa = 0.0
    total_rsl = 0.0

    for bucket in ORDERED_BUCKETS:
        positions = bs.by_bucket(bucket)
        rsa = sum(p.balance for p in positions if p.is_asset)
        rsl = sum(p.balance for p in positions if not p.is_asset)
        gap = rsa - rsl
        cumulative += gap
        total_rsa += rsa
        total_rsl += rsl

        rows.append(GapTableRow(
            bucket=bucket.value,
            rsa=round(rsa, 2),
            rsl=round(rsl, 2),
            gap=round(gap, 2),
            cumulative_gap=round(cumulative, 2),
            gap_ratio=round(gap / total_assets, 6) if total_assets > 0 else 0.0,
        ))

    one_year_gap = sum(r.gap for r in rows if r.bucket in {b.value for b in ONE_YEAR_BUCKETS})

    return LiquidityGapResult(
        gap_table=rows,
        total_rsa=round(total_rsa, 2),
        total_rsl=round(total_rsl, 2),
        net_gap=round(total_rsa - total_rsl, 2),
        one_year_cumulative_gap=round(one_year_gap, 2),
        one_year_gap_ratio=round(one_year_gap / total_assets, 6) if total_assets > 0 else 0.0,
    )
