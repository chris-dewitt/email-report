"""Analytical Greeks for European options under Black-Scholes."""

from __future__ import annotations

import math

from scipy.stats import norm

from vollab.models.option import OptionContract, OptionType
from vollab.models.results import GreeksResult


def compute_greeks(contract: OptionContract) -> GreeksResult:
    S, K, T = contract.spot, contract.strike, contract.expiry
    r, q, sigma = contract.rate, contract.dividend, contract.vol
    sqrt_T = math.sqrt(T)

    d1 = (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    exp_qT = math.exp(-q * T)
    exp_rT = math.exp(-r * T)
    pdf_d1 = norm.pdf(d1)

    if contract.option_type == OptionType.CALL:
        delta = exp_qT * norm.cdf(d1)
        theta = (
            -(S * exp_qT * pdf_d1 * sigma) / (2 * sqrt_T)
            - r * K * exp_rT * norm.cdf(d2)
            + q * S * exp_qT * norm.cdf(d1)
        ) / 365.0
        rho = K * T * exp_rT * norm.cdf(d2) / 100.0
    else:
        delta = exp_qT * (norm.cdf(d1) - 1)
        theta = (
            -(S * exp_qT * pdf_d1 * sigma) / (2 * sqrt_T)
            + r * K * exp_rT * norm.cdf(-d2)
            - q * S * exp_qT * norm.cdf(-d1)
        ) / 365.0
        rho = -K * T * exp_rT * norm.cdf(-d2) / 100.0

    gamma = exp_qT * pdf_d1 / (S * sigma * sqrt_T)
    vega = S * exp_qT * pdf_d1 * sqrt_T / 100.0

    return GreeksResult(
        delta=round(delta, 8),
        gamma=round(gamma, 8),
        theta=round(theta, 8),
        vega=round(vega, 8),
        rho=round(rho, 8),
        method="analytical",
    )
