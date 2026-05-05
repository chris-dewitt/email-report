from balancelab.models.positions import BalanceSheet, Position, RepricingBucket
from balancelab.models.scenarios import (
    ScenarioDefinition,
    RateShock,
    DepositBetaAssumption,
)
from balancelab.core.nii import compute_nii


def _simple_bs() -> BalanceSheet:
    return BalanceSheet(
        name="Test Bank",
        positions=[
            Position(
                id="a1", name="Floating Loan", asset_class="floating_rate_loan",
                balance=1_000_000, rate=0.05, repricing_bucket="3m",
                maturity_years=3.0, is_asset=True,
            ),
            Position(
                id="l1", name="Demand Deposit", asset_class="demand_deposit",
                balance=800_000, rate=0.01, repricing_bucket="1m",
                maturity_years=0.0, is_asset=False,
            ),
        ],
    )


def test_base_case_nii_no_change():
    bs = _simple_bs()
    scenario = ScenarioDefinition(
        id="base", name="Base",
        rate_shock=RateShock(name="flat", parallel_bps=0),
    )
    result = compute_nii(bs, scenario)
    assert result.delta_nii == 0.0
    assert result.base_nii > 0


def test_up_100_increases_nii_asset_sensitive():
    bs = _simple_bs()
    scenario = ScenarioDefinition(
        id="up100", name="Up 100",
        rate_shock=RateShock(name="up", parallel_bps=100),
        deposit_betas=[
            DepositBetaAssumption(asset_class_name="demand_deposit", beta=0.2),
        ],
    )
    result = compute_nii(bs, scenario)
    assert result.delta_nii > 0, "Asset-sensitive bank should benefit from rate increases"
    assert result.shocked_nii > result.base_nii


def test_down_200_decreases_nii_asset_sensitive():
    bs = _simple_bs()
    scenario = ScenarioDefinition(
        id="dn200", name="Down 200",
        rate_shock=RateShock(name="down", parallel_bps=-200),
        deposit_betas=[
            DepositBetaAssumption(asset_class_name="demand_deposit", beta=0.15),
        ],
    )
    result = compute_nii(bs, scenario)
    assert result.delta_nii < 0


def test_nii_drivers_populated():
    bs = _simple_bs()
    scenario = ScenarioDefinition(
        id="up100", name="Up 100",
        rate_shock=RateShock(name="up", parallel_bps=100),
    )
    result = compute_nii(bs, scenario)
    assert len(result.top_drivers) > 0
    assert "position_id" in result.top_drivers[0]


def test_deposit_beta_dampens_liability_repricing():
    bs = _simple_bs()
    full_pass = ScenarioDefinition(
        id="full", name="Full",
        rate_shock=RateShock(name="up", parallel_bps=200),
    )
    sticky = ScenarioDefinition(
        id="sticky", name="Sticky",
        rate_shock=RateShock(name="up", parallel_bps=200),
        deposit_betas=[
            DepositBetaAssumption(asset_class_name="demand_deposit", beta=0.1),
        ],
    )
    full_result = compute_nii(bs, full_pass)
    sticky_result = compute_nii(bs, sticky)
    assert sticky_result.delta_nii > full_result.delta_nii, (
        "Sticky deposits should produce more NII improvement"
    )
