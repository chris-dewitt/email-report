from regimeos.signals.builder import build_signal_vector
from regimeos.signals.sample import get_sample_signals


def test_build_from_z_scores():
    sig = build_signal_vector("2024-01-01", growth_z=0.5, inflation_z=0.2)
    assert sig.growth_z == 0.5
    assert sig.inflation_z == 0.2


def test_build_from_raw_indicators():
    sig = build_signal_vector("2024-01-01", gdp_yoy=3.5, cpi_yoy=4.0, unemployment_rate=3.8)
    assert sig.growth_z > 0
    assert sig.inflation_z > 0
    assert sig.labor_z > 0


def test_sample_signals_non_empty():
    signals = get_sample_signals()
    assert len(signals) >= 10


def test_sample_signals_have_dates():
    signals = get_sample_signals()
    for s in signals:
        assert len(s.date) == 10
