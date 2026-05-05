import pytest
from regimeos.models.regime import SignalVector


@pytest.fixture
def expansion_signal() -> SignalVector:
    return SignalVector(date="2024-01-01", growth_z=0.8, inflation_z=0.1,
                        financial_conditions_z=-0.5, labor_z=0.9, vol_z=-0.3, yield_curve_z=0.3)


@pytest.fixture
def crisis_signal() -> SignalVector:
    return SignalVector(date="2024-01-01", growth_z=-3.5, inflation_z=-1.0,
                        financial_conditions_z=3.0, labor_z=-4.0, vol_z=4.0, yield_curve_z=-1.5)


@pytest.fixture
def overheating_signal() -> SignalVector:
    return SignalVector(date="2024-01-01", growth_z=1.0, inflation_z=2.5,
                        financial_conditions_z=0.5, labor_z=1.5, policy_sentiment=0.9)
