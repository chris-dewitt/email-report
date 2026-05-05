"""Monte Carlo pricing tests — convergence and consistency checks."""

import pytest

from vollab.models.option import OptionContract, OptionType
from vollab.pricing.black_scholes import price_bs
from vollab.pricing.monte_carlo import price_mc


def test_mc_converges_to_bs(atm_call: OptionContract):
    """MC with enough paths should be within 1% of BS."""
    bs_price = price_bs(atm_call).price
    mc_result = price_mc(atm_call, n_paths=500_000, seed=123)
    assert abs(mc_result.price - bs_price) / bs_price < 0.01


def test_mc_put_converges(atm_put: OptionContract):
    bs_price = price_bs(atm_put).price
    mc_result = price_mc(atm_put, n_paths=500_000, seed=456)
    assert abs(mc_result.price - bs_price) / bs_price < 0.01


def test_mc_std_error_decreases_with_paths():
    c = OptionContract(spot=100, strike=100, expiry=1.0, vol=0.20, rate=0.05)
    r1 = price_mc(c, n_paths=10_000, seed=1)
    r2 = price_mc(c, n_paths=200_000, seed=1)
    assert r2.mc_std_error < r1.mc_std_error


def test_mc_reproducible_with_seed():
    c = OptionContract(spot=100, strike=100, expiry=1.0, vol=0.20, rate=0.05)
    r1 = price_mc(c, seed=42)
    r2 = price_mc(c, seed=42)
    assert r1.price == r2.price


def test_antithetic_reduces_variance():
    c = OptionContract(spot=100, strike=100, expiry=1.0, vol=0.20, rate=0.05)
    with_anti = price_mc(c, n_paths=50_000, seed=1, antithetic=True)
    without = price_mc(c, n_paths=50_000, seed=1, antithetic=False)
    assert with_anti.mc_std_error <= without.mc_std_error * 1.1
