"""Analytical tests for Black-Scholes pricing against known values."""

import math

import pytest
from scipy.stats import norm

from vollab.models.option import OptionContract, OptionType
from vollab.pricing.black_scholes import price_bs, bs_call, bs_put, implied_vol


def test_atm_call_known_value(atm_call: OptionContract):
    """ATM call S=K=100, T=1, σ=20%, r=5% should be ~$10.45."""
    result = price_bs(atm_call)
    assert 10.0 < result.price < 11.0


def test_put_call_parity(atm_call: OptionContract):
    """C - P = S·e^{-qT} - K·e^{-rT}"""
    put_contract = atm_call.model_copy(update={"option_type": OptionType.PUT})
    call_price = price_bs(atm_call).price
    put_price = price_bs(put_contract).price
    S, K, r, T = atm_call.spot, atm_call.strike, atm_call.rate, atm_call.expiry
    parity = S - K * math.exp(-r * T)
    assert abs((call_price - put_price) - parity) < 1e-6


def test_deep_itm_call_approaches_intrinsic():
    c = OptionContract(spot=200, strike=100, expiry=0.01, vol=0.20, rate=0.05)
    result = price_bs(c)
    assert abs(result.price - 100.0) < 1.0


def test_deep_otm_call_approaches_zero():
    c = OptionContract(spot=50, strike=100, expiry=0.01, vol=0.20, rate=0.05)
    result = price_bs(c)
    assert result.price < 0.01


def test_higher_vol_increases_call_price():
    c1 = OptionContract(spot=100, strike=100, expiry=1.0, vol=0.15, rate=0.05)
    c2 = OptionContract(spot=100, strike=100, expiry=1.0, vol=0.30, rate=0.05)
    assert price_bs(c2).price > price_bs(c1).price


def test_longer_expiry_increases_call_price():
    c1 = OptionContract(spot=100, strike=100, expiry=0.25, vol=0.20, rate=0.05)
    c2 = OptionContract(spot=100, strike=100, expiry=2.0, vol=0.20, rate=0.05)
    assert price_bs(c2).price > price_bs(c1).price


def test_implied_vol_round_trip():
    c = OptionContract(spot=100, strike=105, expiry=0.5, vol=0.25, rate=0.03)
    market_price = price_bs(c).price
    recovered = implied_vol(market_price, 100, 105, 0.5, 0.03, 0.0, OptionType.CALL)
    assert abs(recovered - 0.25) < 1e-6


def test_price_is_positive(atm_call, atm_put):
    assert price_bs(atm_call).price > 0
    assert price_bs(atm_put).price > 0
