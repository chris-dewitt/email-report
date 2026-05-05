from __future__ import annotations

from fastapi import APIRouter

from vollab.models.option import OptionContract
from vollab.models.results import GreeksResult
from vollab.greeks.analytical import compute_greeks
from vollab.greeks.finite_diff import compute_greeks_fd

router = APIRouter()


@router.post("/analytical", response_model=GreeksResult)
def greeks_analytical(contract: OptionContract) -> GreeksResult:
    return compute_greeks(contract)


@router.post("/fd", response_model=GreeksResult)
def greeks_finite_diff(contract: OptionContract) -> GreeksResult:
    return compute_greeks_fd(contract)


@router.post("/compare", response_model=list[GreeksResult])
def compare_greeks(contract: OptionContract) -> list[GreeksResult]:
    return [compute_greeks(contract), compute_greeks_fd(contract)]
