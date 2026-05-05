from __future__ import annotations

from fastapi import APIRouter, Query

from vollab.models.option import OptionContract
from vollab.models.results import PricingResult
from vollab.pricing.black_scholes import price_bs
from vollab.pricing.monte_carlo import price_mc

router = APIRouter()


@router.post("/bs", response_model=PricingResult)
def price_black_scholes(contract: OptionContract) -> PricingResult:
    return price_bs(contract)


@router.post("/mc", response_model=PricingResult)
def price_monte_carlo(
    contract: OptionContract,
    n_paths: int = Query(default=100_000, ge=1000),
    seed: int = Query(default=42),
) -> PricingResult:
    return price_mc(contract, n_paths=n_paths, seed=seed)


@router.post("/compare", response_model=list[PricingResult])
def compare_methods(contract: OptionContract) -> list[PricingResult]:
    return [price_bs(contract), price_mc(contract)]
