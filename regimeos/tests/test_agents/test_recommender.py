from regimeos.models.regime import RegimeLabel
from regimeos.agents.recommender import generate_recommendation
from regimeos.state.classifier import classify_regime
from regimeos.signals.sample import get_sample_signals
from regimeos.state.engine import run_regime_engine


def test_recommendation_has_actions(expansion_signal):
    state = classify_regime(expansion_signal)
    rec = generate_recommendation(state)
    assert len(rec.actions) > 0


def test_recommendation_has_rationale(expansion_signal):
    state = classify_regime(expansion_signal)
    rec = generate_recommendation(state)
    assert len(rec.rationale) > 20
    assert state.label.value in rec.rationale


def test_recommendation_pending_approval(expansion_signal):
    state = classify_regime(expansion_signal)
    rec = generate_recommendation(state)
    assert rec.approval_status == "pending"


def test_crisis_recommends_hedges(crisis_signal):
    from regimeos.models.recommendation import RiskAction
    state = classify_regime(crisis_signal)
    rec = generate_recommendation(state)
    assert RiskAction.INCREASE_HEDGES in rec.actions or RiskAction.ADD_LIQUIDITY_BUFFER in rec.actions


def test_overheating_recommends_duration_reduction(overheating_signal):
    from regimeos.models.recommendation import RiskAction
    state = classify_regime(overheating_signal)
    rec = generate_recommendation(state)
    assert RiskAction.REDUCE_DURATION in rec.actions


def test_recommendation_has_watchlist(expansion_signal):
    state = classify_regime(expansion_signal)
    rec = generate_recommendation(state)
    assert len(rec.watchlist) > 0


def test_full_pipeline():
    signals = get_sample_signals()
    states, _ = run_regime_engine(signals)
    rec = generate_recommendation(states[-1])
    assert rec.regime == states[-1].label.value
    assert rec.confidence == states[-1].confidence
