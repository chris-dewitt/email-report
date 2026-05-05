"""Shared API state — in-memory balance sheet holder for the demo."""

from __future__ import annotations

from balancelab.models.positions import BalanceSheet

_current_bs: BalanceSheet | None = None


def get_balance_sheet() -> BalanceSheet | None:
    return _current_bs


def set_balance_sheet(bs: BalanceSheet) -> None:
    global _current_bs
    _current_bs = bs
