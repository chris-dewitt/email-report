"""Sample signal data covering multiple historical regime episodes."""

from __future__ import annotations

from regimeos.models.regime import SignalVector


def get_sample_signals() -> list[SignalVector]:
    return [
        SignalVector(date="2019-01-01", growth_z=0.6, inflation_z=-0.2, financial_conditions_z=-0.5,
                     labor_z=0.8, policy_sentiment=-0.2, vol_z=0.3, yield_curve_z=0.1),
        SignalVector(date="2019-07-01", growth_z=0.3, inflation_z=0.0, financial_conditions_z=-0.3,
                     labor_z=0.9, policy_sentiment=-0.5, vol_z=-0.2, yield_curve_z=-0.1),
        SignalVector(date="2020-01-01", growth_z=0.4, inflation_z=0.1, financial_conditions_z=-0.2,
                     labor_z=1.0, policy_sentiment=0.0, vol_z=0.1, yield_curve_z=0.0),
        SignalVector(date="2020-04-01", growth_z=-4.0, inflation_z=-1.5, financial_conditions_z=2.5,
                     labor_z=-4.5, policy_sentiment=-1.0, vol_z=3.5, yield_curve_z=-0.5),
        SignalVector(date="2020-10-01", growth_z=-1.5, inflation_z=-0.5, financial_conditions_z=0.5,
                     labor_z=-2.0, policy_sentiment=-1.0, vol_z=1.5, yield_curve_z=0.2),
        SignalVector(date="2021-04-01", growth_z=1.8, inflation_z=0.8, financial_conditions_z=-1.0,
                     labor_z=0.5, policy_sentiment=-0.8, vol_z=-0.5, yield_curve_z=0.8),
        SignalVector(date="2021-10-01", growth_z=1.5, inflation_z=2.0, financial_conditions_z=-0.5,
                     labor_z=1.0, policy_sentiment=-0.3, vol_z=0.0, yield_curve_z=0.6),
        SignalVector(date="2022-04-01", growth_z=0.2, inflation_z=2.5, financial_conditions_z=0.8,
                     labor_z=1.2, policy_sentiment=0.8, vol_z=1.0, yield_curve_z=-0.5),
        SignalVector(date="2022-10-01", growth_z=-0.5, inflation_z=2.0, financial_conditions_z=1.5,
                     labor_z=0.8, policy_sentiment=1.0, vol_z=1.5, yield_curve_z=-1.2),
        SignalVector(date="2023-04-01", growth_z=0.2, inflation_z=0.8, financial_conditions_z=1.0,
                     labor_z=0.5, policy_sentiment=0.6, vol_z=0.5, yield_curve_z=-1.0),
        SignalVector(date="2023-10-01", growth_z=0.5, inflation_z=0.3, financial_conditions_z=0.8,
                     labor_z=0.6, policy_sentiment=0.3, vol_z=0.2, yield_curve_z=-0.8),
        SignalVector(date="2024-04-01", growth_z=0.7, inflation_z=0.2, financial_conditions_z=0.5,
                     labor_z=0.4, policy_sentiment=0.1, vol_z=-0.1, yield_curve_z=-0.3),
        SignalVector(date="2024-10-01", growth_z=0.8, inflation_z=-0.1, financial_conditions_z=0.2,
                     labor_z=0.3, policy_sentiment=-0.2, vol_z=-0.2, yield_curve_z=0.1),
    ]
