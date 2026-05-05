"""Build a SignalVector from raw macro/market observations."""

from __future__ import annotations

from regimeos.models.regime import SignalVector


def build_signal_vector(
    date: str,
    gdp_yoy: float | None = None,
    cpi_yoy: float | None = None,
    unemployment_rate: float | None = None,
    fed_funds_rate: float | None = None,
    ten_year_yield: float | None = None,
    two_year_yield: float | None = None,
    vix: float | None = None,
    policy_sentiment: float = 0.0,
    growth_z: float | None = None,
    inflation_z: float | None = None,
    financial_conditions_z: float | None = None,
    labor_z: float | None = None,
    vol_z: float | None = None,
    yield_curve_z: float | None = None,
) -> SignalVector:
    """Accept either raw indicators or pre-computed z-scores.
    Pre-computed z-scores take precedence over raw indicators.
    """
    def _z(raw: float | None, mean: float, std: float) -> float:
        if raw is None:
            return 0.0
        return (raw - mean) / std if std > 0 else 0.0

    g_z = growth_z if growth_z is not None else _z(gdp_yoy, 2.5, 2.0)
    i_z = inflation_z if inflation_z is not None else _z(cpi_yoy, 2.5, 1.5)
    l_z = labor_z if labor_z is not None else _z(
        (4.5 - unemployment_rate) if unemployment_rate is not None else None, 0.0, 1.0
    )

    yc = None
    if ten_year_yield is not None and two_year_yield is not None:
        yc = ten_year_yield - two_year_yield
    yc_z = yield_curve_z if yield_curve_z is not None else _z(yc, 1.0, 0.75)

    v_z = vol_z if vol_z is not None else _z(vix, 20.0, 8.0)

    fc_z = financial_conditions_z
    if fc_z is None and fed_funds_rate is not None:
        fc_z = _z(fed_funds_rate, 2.5, 1.5)
    fc_z = fc_z or 0.0

    return SignalVector(
        date=date,
        growth_z=round(g_z, 3),
        inflation_z=round(i_z, 3),
        financial_conditions_z=round(fc_z, 3),
        labor_z=round(l_z, 3),
        policy_sentiment=round(policy_sentiment, 3),
        vol_z=round(v_z, 3),
        yield_curve_z=round(yc_z, 3),
    )
