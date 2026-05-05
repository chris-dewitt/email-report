"""Volatility surface construction and interpolation.

Builds a discrete vol surface from market quotes and provides
bilinear interpolation for arbitrary (strike, expiry) queries.
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import RectBivariateSpline

from vollab.models.results import SurfacePoint


def build_surface(
    strikes: list[float],
    expiries: list[float],
    vols: list[list[float]],
    spot: float = 100.0,
) -> list[SurfacePoint]:
    points = []
    for i, T in enumerate(expiries):
        for j, K in enumerate(strikes):
            points.append(SurfacePoint(
                strike=K,
                expiry=T,
                vol=vols[i][j],
                moneyness=round(K / spot, 4),
            ))
    return points


def interpolate_vol(
    strikes: list[float],
    expiries: list[float],
    vols: list[list[float]],
    query_strike: float,
    query_expiry: float,
) -> float:
    vol_array = np.array(vols)
    spline = RectBivariateSpline(expiries, strikes, vol_array, kx=1, ky=1)
    result = float(spline(query_expiry, query_strike)[0, 0])
    return max(result, 0.001)


def sample_skew_surface(spot: float = 100.0) -> tuple[list[float], list[float], list[list[float]]]:
    """Generate a stylized equity vol surface with skew."""
    strikes = [round(spot * m, 2) for m in [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20]]
    expiries = [0.083, 0.25, 0.5, 1.0, 2.0]

    base_vol = 0.20
    vols = []
    for T in expiries:
        row = []
        term_adj = -0.02 * (T - 0.5)
        for K in strikes:
            moneyness = K / spot
            skew = 0.12 * (1.0 - moneyness)
            smile = 0.03 * (moneyness - 1.0) ** 2
            vol = base_vol + skew + smile + term_adj
            row.append(round(max(vol, 0.05), 4))
        vols.append(row)

    return strikes, expiries, vols
