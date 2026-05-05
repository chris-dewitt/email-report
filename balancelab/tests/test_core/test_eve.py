from balancelab.models.positions import BalanceSheet, Position
from balancelab.models.scenarios import ScenarioDefinition, RateShock
from balancelab.core.eve import compute_eve


def _duration_gap_bs() -> BalanceSheet:
    return BalanceSheet(
        name="Duration Test",
        positions=[
            Position(
                id="a1", name="Long Bond", asset_class="investment_security",
                balance=1_000_000, rate=0.04, repricing_bucket="10y",
                maturity_years=10.0, is_asset=True,
            ),
            Position(
                id="l1", name="Short Deposit", asset_class="term_deposit",
                balance=800_000, rate=0.03, repricing_bucket="1y",
                maturity_years=1.0, is_asset=False,
            ),
        ],
    )


def test_eve_base_case():
    bs = _duration_gap_bs()
    scenario = ScenarioDefinition(
        id="base", name="Base",
        rate_shock=RateShock(name="flat", parallel_bps=0),
    )
    result = compute_eve(bs, scenario)
    assert result.delta_eve == 0.0
    assert result.base_eve != 0


def test_positive_duration_gap_loses_eve_on_rate_rise():
    bs = _duration_gap_bs()
    scenario = ScenarioDefinition(
        id="up200", name="Up 200",
        rate_shock=RateShock(name="up", parallel_bps=200),
    )
    result = compute_eve(bs, scenario)
    assert result.duration_gap > 0, "Asset duration should exceed liability duration"
    assert result.delta_eve < 0, "Positive duration gap loses EVE when rates rise"


def test_eve_improves_on_rate_decline_with_positive_gap():
    bs = _duration_gap_bs()
    scenario = ScenarioDefinition(
        id="dn100", name="Down 100",
        rate_shock=RateShock(name="down", parallel_bps=-100),
    )
    result = compute_eve(bs, scenario)
    assert result.delta_eve > 0


def test_duration_values_reasonable():
    bs = _duration_gap_bs()
    scenario = ScenarioDefinition(
        id="base", name="Base",
        rate_shock=RateShock(name="flat", parallel_bps=0),
    )
    result = compute_eve(bs, scenario)
    assert 0 < result.asset_duration < 20
    assert 0 < result.liability_duration < 20
