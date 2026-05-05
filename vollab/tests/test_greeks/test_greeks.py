"""Greeks tests — analytical vs finite-difference consistency."""

import pytest

from vollab.models.option import OptionContract, OptionType
from vollab.greeks.analytical import compute_greeks
from vollab.greeks.finite_diff import compute_greeks_fd


def test_call_delta_between_0_and_1(atm_call: OptionContract):
    g = compute_greeks(atm_call)
    assert 0 < g.delta < 1


def test_put_delta_between_neg1_and_0(atm_put: OptionContract):
    g = compute_greeks(atm_put)
    assert -1 < g.delta < 0


def test_gamma_positive(atm_call: OptionContract):
    g = compute_greeks(atm_call)
    assert g.gamma > 0


def test_vega_positive(atm_call: OptionContract):
    g = compute_greeks(atm_call)
    assert g.vega > 0


def test_theta_negative_for_long_call(atm_call: OptionContract):
    g = compute_greeks(atm_call)
    assert g.theta < 0


def test_analytical_vs_fd_delta(atm_call: OptionContract):
    an = compute_greeks(atm_call)
    fd = compute_greeks_fd(atm_call)
    assert abs(an.delta - fd.delta) < 0.01


def test_analytical_vs_fd_gamma(atm_call: OptionContract):
    an = compute_greeks(atm_call)
    fd = compute_greeks_fd(atm_call)
    assert abs(an.gamma - fd.gamma) < 0.001


def test_analytical_vs_fd_vega(atm_call: OptionContract):
    an = compute_greeks(atm_call)
    fd = compute_greeks_fd(atm_call)
    assert abs(an.vega - fd.vega) < 0.01


def test_itm_call_delta_near_1(itm_call: OptionContract):
    deep = itm_call.model_copy(update={"spot": 150})
    g = compute_greeks(deep)
    assert g.delta > 0.9


def test_put_call_delta_relationship(atm_call: OptionContract, atm_put: OptionContract):
    """For European options: Δ_call - Δ_put ≈ e^{-qT}"""
    dc = compute_greeks(atm_call).delta
    dp = compute_greeks(atm_put).delta
    assert abs((dc - dp) - 1.0) < 0.01
