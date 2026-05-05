from regimeos.signals.sample import get_sample_signals
from regimeos.state.engine import run_regime_engine


def test_engine_produces_state_per_signal():
    signals = get_sample_signals()
    states, _ = run_regime_engine(signals)
    assert len(states) == len(signals)


def test_engine_detects_covid_crisis():
    signals = get_sample_signals()
    states, transitions = run_regime_engine(signals)
    labels = [s.label.value for s in states]
    assert "crisis" in labels or "contraction" in labels


def test_transitions_are_fewer_than_states():
    signals = get_sample_signals()
    states, transitions = run_regime_engine(signals)
    assert len(transitions) <= len(states)


def test_transitions_have_date_and_labels():
    signals = get_sample_signals()
    _, transitions = run_regime_engine(signals)
    for t in transitions:
        assert t.date
        assert t.from_regime != t.to_regime
