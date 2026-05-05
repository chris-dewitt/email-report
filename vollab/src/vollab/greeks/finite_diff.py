"""Finite-difference Greeks — works with any pricing function."""

from __future__ import annotations

from vollab.models.option import OptionContract
from vollab.models.results import GreeksResult
from vollab.pricing.black_scholes import price_bs


def compute_greeks_fd(
    contract: OptionContract,
    dS: float = 0.01,
    dT: float = 1 / 365,
    dSigma: float = 0.01,
    dR: float = 0.0001,
) -> GreeksResult:
    base = price_bs(contract).price

    up = contract.model_copy(update={"spot": contract.spot * (1 + dS)})
    dn = contract.model_copy(update={"spot": contract.spot * (1 - dS)})
    p_up = price_bs(up).price
    p_dn = price_bs(dn).price
    bump = contract.spot * dS

    delta = (p_up - p_dn) / (2 * bump)
    gamma = (p_up - 2 * base + p_dn) / (bump**2)

    t_dn = contract.model_copy(update={"expiry": max(contract.expiry - dT, 1e-6)})
    theta = (price_bs(t_dn).price - base) / dT / 365.0

    v_up = contract.model_copy(update={"vol": contract.vol + dSigma})
    vega = (price_bs(v_up).price - base) / (dSigma * 100)

    r_up = contract.model_copy(update={"rate": contract.rate + dR})
    rho = (price_bs(r_up).price - base) / (dR * 100)

    return GreeksResult(
        delta=round(delta, 8),
        gamma=round(gamma, 8),
        theta=round(theta, 8),
        vega=round(vega, 8),
        rho=round(rho, 8),
        method="finite_difference",
    )
