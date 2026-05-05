# RegimeOS

**Regime detection and decision-support orchestration engine for macro, policy, and market-risk synthesis.**

---

## Business Case

Senior decision-makers often need one answer to a hard question: *what regime are we in, what changed, and what should we focus on?* RegimeOS combines macro signal composites, policy-language indicators (from FedLens), and market behavior into an explainable state machine with portfolio and risk guidance — all requiring human approval before any action is taken.

---

## What It Does

| Capability | Description |
|---|---|
| Signal ingestion | Accepts macro z-scores or raw indicators (GDP, CPI, unemployment, VIX, yield curve) |
| Regime classification | Probabilistic regime assignment across 6 states with confidence and driver attribution |
| Transition detection | Flags regime shifts with key signal drivers |
| Recommendation agent | Converts regime state to risk action playbook (pending human approval) |
| Explainer agent | LLM-powered narrative for investment committees (Ollama, with structured fallback) |
| HITL approval queue | All recommendations are "pending" until explicitly approved or rejected |
| Atlas integration | Designed to consume macro feature blocks exported from Atlas |
| FedLens integration | Policy sentiment signal feeds from FedLens event-study outputs |

---

## Regime States

| Regime | Signal Profile |
|---|---|
| **Expansion** | Growth ↑, inflation moderate, conditions easy, labor strong |
| **Overheating** | Growth ↑, inflation ↑↑, conditions tightening, policy hawkish |
| **Slowdown** | Growth ↓, conditions tightening, labor softening |
| **Contraction** | Growth ↓↓, inflation ↓, conditions tight, labor weakening |
| **Crisis** | Growth ↓↓↓, vol ↑↑, conditions very tight |
| **Transition** | Mixed signals, low confidence across regimes |

---

## Key Mathematics

**State probability (softmax over regime affinity scores)**
```
p(z_t = k | x_t) = exp(a_k(x_t)) / Σⱼ exp(aⱼ(x_t))
```

where `a_k(x_t) = −Σᵢ (xᵢ − μᵢᵏ)²` is the negative squared distance of the observed signal vector from regime k's prototype.

This is interpretable: high confidence = the signal vector sits close to one regime's prototype and far from all others. Low confidence = the vector is equidistant between multiple prototypes, indicating a transition or ambiguous period.

---

## Architecture

```
Signal Vector (growth_z, inflation_z, vol_z, yield_curve_z, policy_sentiment, ...)
    └─► State Classifier (softmax probabilities, regime label, confidence, drivers)
            └─► Regime Engine (time-series: transition detection, history)
                    ├─► Recommendation Agent (playbook → risk actions, watchlist)
                    └─► Explainer Agent (LLM narrative, structured fallback)
                                └─► Approval Queue (pending → approved/rejected)
```

**Cross-project integration:**
- `Atlas` → exports macro feature z-scores → consumed by `signals.builder`
- `FedLens` → exports `policy_sentiment` from hawkish/dovish scoring → fed into `SignalVector`

**Stack:** Python · FastAPI · Pydantic · scikit-learn · Typer · (Ollama optional)

---

## Local Setup

```bash
git clone <repo>
cd regimeos
pip install -e ".[dev]"

# Run the regime engine and display current state
regimeos refresh

# Score an ad-hoc signal vector
regimeos score-state --growth-z 0.8 --inflation-z 2.5 --financial-conditions-z 0.5

# Generate a regime briefing
regimeos explain "What changed since the last overheating period?"

# Export a Markdown regime note
regimeos publish-note --output regime_q4_2024.md

# Start API
regimeos serve
# → http://localhost:8003/docs
```

---

## CLI Reference

| Command | Description |
|---|---|
| `regimeos refresh` | Run engine on sample data, display state + transitions |
| `regimeos score-state` | Classify a custom signal vector |
| `regimeos explain` | LLM narrative briefing |
| `regimeos publish-note` | Export Markdown regime note |
| `regimeos serve` | Start FastAPI on port 8003 |

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Regime labels available |
| `/signals` | GET | Sample signal history |
| `/signals/latest` | GET | Most recent signal vector |
| `/state` | GET | Current regime state + probabilities |
| `/state/history` | GET | Full state history |
| `/state/uncertainty` | GET | Probability distribution over regimes |
| `/state/classify` | POST | Classify a custom signal |
| `/recommendations` | GET | Current recommendation (pending approval) |
| `/recommendations/explain` | GET | LLM-powered briefing |
| `/approval-queue` | GET | List pending recommendations |
| `/approval-queue/approve/{id}` | POST | Approve a recommendation |
| `/approval-queue/reject/{id}` | POST | Reject a recommendation |

---

## Test Suite

```bash
pytest -v   # 34 tests
```

Tests cover: regime classification correctness (expansion, crisis, overheating), confidence bounds, probability normalization, transition detection, full pipeline integration, recommendation playbook correctness, and all API endpoints.

---

## Limitations and Future Work

- Regime classifier uses rule-based softmax prototypes; production would add HMM or Bayesian state-space models
- Signal z-scores are manually set in the sample; production connects directly to Atlas API
- Policy sentiment is a scalar placeholder; FedLens provides a richer multi-document signal
- Walk-forward evaluation and backtest-lite regime-to-action analysis are stretch goals
- No portfolio optimization or position-level risk templates yet

---

## Production Path

Production deployment would add: real-time Atlas and FedLens signal feeds, hidden Markov model or regime-switching VAR for state estimation, portfolio-level risk impact templates by regime, walk-forward evaluation of regime-signal quality, and an enterprise approval workflow (email/Slack notification, audit trail).
