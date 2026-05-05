"""Black-Scholes-Merton analytical pricing.

Under geometric Brownian motion:  dS_t = μ S_t dt + σ S_t dW_t

The European call price is:  C = S e^{-qT} N(d₁) - K e^{-rT} N(d₂)
where d₁ = [ln(S/K) + (r - q + σ²/2)T] / (σ√T)
      d₂ = d₁ - σ√T

Put price via put-call parity:  P = K e^{-rT} N(-d₂) - S e^{-qT} N(-d₁)
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import norm

from vollab.models.option import OptionContract, OptionType
from vollab.models.results import PricingResult


def _d1d2(S: float, K: float, T: float, r: float, q: float, sigma: float) -> tuple[float, float]:
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return d1, d2


def bs_call(S: float, K: float, T: float, r: float, q: float, sigma: float) -> float:
    d1, d2 = _d1d2(S, K, T, r, q, sigma)
    return S * math.exp(-q * T) * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)


def bs_put(S: float, K: float, T: float, r: float, q: float, sigma: float) -> float:
    d1, d2 = _d1d2(S, K, T, r, q, sigma)
    return K * math.exp(-r * T) * norm.cdf(-d2) - S * math.exp(-q * T) * norm.cdf(-d1)


def price_bs(contract: OptionContract) -> PricingResult:
    S, K, T = contract.spot, contract.strike, contract.expiry
    r, q, sigma = contract.rate, contract.dividend, contract.vol

    if contract.option_type == OptionType.CALL:
        price = bs_call(S, K, T, r, q, sigma)
        intrinsic = max(S - K, 0.0)
    else:
        price = bs_put(S, K, T, r, q, sigma)
        intrinsic = max(K - S, 0.0)

    return PricingResult(
        price=round(price * contract.notional, 8),
        method="black_scholes",
        option_type=contract.option_type.value,
        spot=S,
        strike=K,
        expiry=T,
        vol=sigma,
        rate=r,
        intrinsic=round(intrinsic * contract.notional, 8),
        time_value=round((price - intrinsic) * contract.notional, 8),
    )


def implied_vol(
    market_price: float,
    S: float, K: float, T: float, r: float, q: float,
    option_type: OptionType = OptionType.CALL,
    tol: float = 1e-8,
    max_iter: int = 100,
) -> float:
    """Newton-Raphson implied volatility solver."""
    sigma = 0.25
    pricer = bs_call if option_type == OptionType.CALL else bs_put

    for _ in range(max_iter):
        price = pricer(S, K, T, r, q, sigma)
        d1, _ = _d1d2(S, K, T, r, q, sigma)
        vega = S * math.exp(-q * T) * norm.pdf(d1) * math.sqrt(T)
        if vega < 1e-12:
            break
        sigma -= (price - market_price) / vega
        sigma = max(sigma, 1e-6)
        if abs(price - market_price) < tol:
            break

    return sigma
