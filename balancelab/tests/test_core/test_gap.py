import json
from pathlib import Path

from balancelab.models.positions import BalanceSheet
from balancelab.core.gap import compute_liquidity_gap

SAMPLE = Path(__file__).parent.parent.parent / "sample_data" / "sample_balance_sheet.json"


def test_gap_table_has_all_buckets():
    bs = BalanceSheet.model_validate(json.loads(SAMPLE.read_text(encoding="utf-8")))
    result = compute_liquidity_gap(bs)
    assert len(result.gap_table) == 11  # all repricing buckets


def test_total_rsa_rsl_match_balance_sheet():
    bs = BalanceSheet.model_validate(json.loads(SAMPLE.read_text(encoding="utf-8")))
    result = compute_liquidity_gap(bs)
    assert abs(result.total_rsa + result.total_rsl - (bs.total_assets + bs.total_liabilities)) < 1.0


def test_cumulative_gap_sums_correctly():
    bs = BalanceSheet.model_validate(json.loads(SAMPLE.read_text(encoding="utf-8")))
    result = compute_liquidity_gap(bs)
    running = 0.0
    for row in result.gap_table:
        running += row.gap
        assert abs(row.cumulative_gap - running) < 0.01


def test_one_year_gap_ratio_bounded():
    bs = BalanceSheet.model_validate(json.loads(SAMPLE.read_text(encoding="utf-8")))
    result = compute_liquidity_gap(bs)
    assert -1.0 <= result.one_year_gap_ratio <= 1.0
