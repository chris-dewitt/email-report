"""Scenario PnL grid — stress an option across spot and vol shifts."""

from __future__ import annotations

from vollab.models.option import OptionContract
from vollab.models.results import ScenarioPnL
from vollab.pricing.black_scholes import price_bs


def compute_scenario_pnl(
    contract: OptionContract,
    spot_shifts: list[float] | None = None,
    vol_shifts: list[float] | None = None,
) -> list[ScenarioPnL]:
    if spot_shifts is None:
        spot_shifts = [-0.20, -0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15, 0.20]
    if vol_shifts is None:
        vol_shifts = [-0.05, -0.025, 0.0, 0.025, 0.05]

    base_price = price_bs(contract).price
    results = []

    for ds in spot_shifts:
        for dv in vol_shifts:
            new_spot = contract.spot * (1 + ds)
            new_vol = max(contract.vol + dv, 0.01)
            shifted = contract.model_copy(update={"spot": new_spot, "vol": new_vol})
            new_price = price_bs(shifted).price
            pnl = new_price - base_price
            pnl_pct = (pnl / base_price * 100) if base_price != 0 else 0.0

            results.append(ScenarioPnL(
                spot_shift=ds,
                vol_shift=dv,
                base_price=round(base_price, 6),
                new_price=round(new_price, 6),
                pnl=round(pnl, 6),
                pnl_pct=round(pnl_pct, 4),
            ))

    return results
