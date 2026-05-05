from balancelab.scenarios.catalog import ScenarioCatalog
from balancelab.models.scenarios import ScenarioDefinition, RateShock


def test_standard_scenarios_loaded():
    cat = ScenarioCatalog()
    assert len(cat.list_scenarios()) >= 7


def test_get_by_id():
    cat = ScenarioCatalog()
    s = cat.get("up_200")
    assert s is not None
    assert s.rate_shock.parallel_bps == 200


def test_add_custom_scenario():
    cat = ScenarioCatalog()
    custom = ScenarioDefinition(
        id="custom_1", name="Custom Shock",
        rate_shock=RateShock(name="custom", parallel_bps=150),
    )
    cat.add(custom)
    assert cat.get("custom_1") is not None


def test_remove_scenario():
    cat = ScenarioCatalog()
    assert cat.remove("base") is True
    assert cat.get("base") is None


def test_shock_for_bucket_twist():
    cat = ScenarioCatalog()
    steep = cat.get("steepener")
    assert steep is not None
    from balancelab.models.positions import RepricingBucket
    short_shock = steep.rate_shock.shock_for_bucket(RepricingBucket.M3)
    long_shock = steep.rate_shock.shock_for_bucket(RepricingBucket.Y10)
    assert short_shock < 0
    assert long_shock > 0
