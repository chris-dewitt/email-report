import pytest
from vollab.models.option import OptionContract, OptionType


@pytest.fixture
def atm_call() -> OptionContract:
    return OptionContract(spot=100, strike=100, expiry=1.0, vol=0.20, rate=0.05)


@pytest.fixture
def atm_put() -> OptionContract:
    return OptionContract(
        spot=100, strike=100, expiry=1.0, vol=0.20, rate=0.05,
        option_type=OptionType.PUT,
    )


@pytest.fixture
def itm_call() -> OptionContract:
    return OptionContract(spot=110, strike=100, expiry=1.0, vol=0.20, rate=0.05)


@pytest.fixture
def otm_call() -> OptionContract:
    return OptionContract(spot=90, strike=100, expiry=1.0, vol=0.20, rate=0.05)
