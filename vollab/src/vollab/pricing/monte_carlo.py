"""Monte Carlo option pricing via risk-neutral simulation.

Simulates GBM paths:  S_T = S_0 exp[(r - q - σ²/2)T + σ√T Z]
where Z ~ N(0,1), then discounts the expected payoff.
"""

from __future__ import annotations

import math

import numpy as np

from vollab.models.option import OptionContract, OptionType
from vollab.models.results import PricingResult
from vollab.settings import settings


def _payoff(S_T: np.ndarray, K: float, option_type: OptionType) -> np.ndarray:
    if option_type == OptionType.CALL:
        return np.maximum(S_T - K, 0.0)
    return np.maximum(K - S_T, 0.0)


def price_mc(
    contract: OptionContract,
    n_paths: int | None = None,
    seed: int | None = None,
    antithetic: bool = True,
) -> PricingResult:
    n = n_paths or settings.mc_default_paths
    rng = np.random.default_rng(seed or settings.mc_default_seed)

    S, K, T = contract.spot, contract.strike, contract.expiry
    r, q, sigma = contract.rate, contract.dividend, contract.vol

    drift = (r - q - 0.5 * sigma**2) * T
    diffusion = sigma * math.sqrt(T)

    z = rng.standard_normal(n)
    if antithetic:
        z = np.concatenate([z, -z])

    S_T = S * np.exp(drift + diffusion * z)
    payoffs = _payoff(S_T, K, contract.option_type)
    discounted = math.exp(-r * T) * payoffs

    price = float(np.mean(discounted))
    std_error = float(np.std(discounted) / math.sqrt(len(discounted)))

    intrinsic = max(S - K, 0.0) if contract.option_type == OptionType.CALL else max(K - S, 0.0)

    return PricingResult(
        price=round(price * contract.notional, 8),
        method="monte_carlo",
        option_type=contract.option_type.value,
        spot=S,
        strike=K,
        expiry=T,
        vol=sigma,
        rate=r,
        intrinsic=round(intrinsic * contract.notional, 8),
        time_value=round((price - intrinsic) * contract.notional, 8),
        mc_std_error=round(std_error * contract.notional, 8),
        mc_paths=len(z),
    )
