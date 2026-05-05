from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from balancelab.models.positions import BalanceSheet, Position
from api.deps import get_balance_sheet, set_balance_sheet

router = APIRouter()


class BalanceSheetSummary(BaseModel):
    name: str
    as_of_date: str
    total_assets: float
    total_liabilities: float
    equity: float
    position_count: int


@router.get("", response_model=BalanceSheetSummary)
def get_positions_summary() -> BalanceSheetSummary:
    bs = get_balance_sheet()
    if bs is None:
        raise HTTPException(404, "No balance sheet loaded. POST to /positions to upload.")
    return BalanceSheetSummary(
        name=bs.name,
        as_of_date=bs.as_of_date,
        total_assets=bs.total_assets,
        total_liabilities=bs.total_liabilities,
        equity=bs.equity,
        position_count=len(bs.positions),
    )


@router.get("/detail", response_model=list[Position])
def get_positions_detail() -> list[Position]:
    bs = get_balance_sheet()
    if bs is None:
        raise HTTPException(404, "No balance sheet loaded.")
    return bs.positions


@router.post("", response_model=BalanceSheetSummary)
def upload_balance_sheet(bs: BalanceSheet) -> BalanceSheetSummary:
    set_balance_sheet(bs)
    return BalanceSheetSummary(
        name=bs.name,
        as_of_date=bs.as_of_date,
        total_assets=bs.total_assets,
        total_liabilities=bs.total_liabilities,
        equity=bs.equity,
        position_count=len(bs.positions),
    )
