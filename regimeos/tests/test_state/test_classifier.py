from regimeos.models.regime import RegimeLabel, SignalVector
from regimeos.state.classifier import classify_regime


def test_expansion_signal_classified_correctly(expansion_signal: SignalVector):
    state = classify_regime(expansion_signal)
    assert state.label == RegimeLabel.EXPANSION


def test_crisis_signal_classified_correctly(crisis_signal: SignalVector):
    state = classify_regime(crisis_signal)
    assert state.label == RegimeLabel.CRISIS


def test_overheating_signal_classified(overheating_signal: SignalVector):
    state = classify_regime(overheating_signal)
    assert state.label == RegimeLabel.OVERHEATING


def test_confidence_between_0_and_1(expansion_signal: SignalVector):
    state = classify_regime(expansion_signal)
    assert 0 < state.confidence <= 1.0


def test_probabilities_sum_to_one(expansion_signal: SignalVector):
    state = classify_regime(expansion_signal)
    total = sum(state.probabilities.values())
    assert abs(total - 1.0) < 1e-3


def test_probabilities_cover_all_regimes(expansion_signal: SignalVector):
    state = classify_regime(expansion_signal)
    labels = {r.value for r in RegimeLabel}
    assert labels == set(state.probabilities.keys())


def test_transition_detected_when_regime_changes():
    sig1 = SignalVector(date="2024-01-01", growth_z=0.8, inflation_z=0.1,
                        financial_conditions_z=-0.5, labor_z=0.9)
    sig2 = SignalVector(date="2024-04-01", growth_z=-3.0, inflation_z=-1.0,
                        financial_conditions_z=2.5, labor_z=-4.0, vol_z=3.5)
    s1 = classify_regime(sig1)
    s2 = classify_regime(sig2, s1)
    assert s2.transition_detected
    assert s2.previous_label == s1.label


def test_no_transition_when_stable(expansion_signal: SignalVector):
    s1 = classify_regime(expansion_signal)
    s2 = classify_regime(expansion_signal, s1)
    assert not s2.transition_detected


def test_drivers_populated(expansion_signal: SignalVector):
    state = classify_regime(expansion_signal)
    assert len(state.drivers) > 0
    assert "signal" in state.drivers[0]
