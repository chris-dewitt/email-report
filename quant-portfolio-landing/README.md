# Quant Finance × Data Science Portfolio

**Five flagship projects at the intersection of quantitative finance, data science, and enterprise AI.**

> Built for Quant/Risk/Trading Managing Directors and internal Enterprise AI / Strategy teams.

---

## Portfolio Thesis

Modern finance teams need builders who can combine rigorous quantitative methods, production-grade software, and agentic AI workflows inside controlled, explainable systems.

This suite proves that across five distinct capability layers — each a standalone project, together a coherent platform.

---

## The Suite

| Project | Role | AI | Math | Stack |
|---|---|---|---|---|
| [**Atlas**](../atlas/) | Macro intelligence platform | Medium | Medium | Python · FRED · DuckDB · FastAPI |
| [**FedLens**](../fedlens/) | Fed NLP and market-reaction copilot | High | Medium | Python · FAISS · sentence-transformers |
| [**BalanceLab**](../balancelab/) | ALM, NII, EVE, scenario analytics | High | Med-High | Python · FastAPI · Pydantic |
| [**VolLab**](../vollab/) | Derivatives and stochastic risk lab | Low | High | Python · NumPy · SciPy |
| [**RegimeOS**](../regimeos/) | Regime detection and decision-support | High | Med-High | Python · scikit-learn · FastAPI |

---

## Capability Map

```
                     ATLAS (macro data backbone)
                      ↓ feature z-scores
FEDLENS ─────────→ REGIMEOS ← market signals
(policy sentiment)     ↓
                  Recommendation + HITL approval
                  
BALANCELAB ────── internal risk tool (bank ALM)
VOLLAB     ────── math flagship (derivatives)
```

**Atlas** exports macro z-scores → **RegimeOS** ingests them as signal inputs.
**FedLens** exports policy-sentiment scores → **RegimeOS** uses them as a `policy_sentiment` signal.
**BalanceLab** and **VolLab** are standalone — their outputs feed into portfolio risk notes.

---

## What Each Project Proves

### Atlas — Data Engineering + Systems Discipline
- End-to-end ETL pipeline (FRED + yfinance → bronze/silver/gold parquet)
- Feature engineering at scale: 36 series × N transforms = 100+ features
- DuckDB embedded OLAP, FastAPI serving, CLI tooling
- LLM-powered macro briefing with citation extraction

### FedLens — LLM Systems + NLP Depth
- Full document corpus (59+ FOMC statements), semantic search via FAISS
- Event-study engine: abnormal returns AR_t = R_t − E[R_t] around policy timestamps
- RAG-based research copilot with structured citations and HITL review
- Embedding drift tracking across the hiking/easing cycle

### BalanceLab — Institutional Risk Modeling
- ΔNII ≈ Σ (RSA_i − RSL_i) × Δr_i with deposit-beta pass-through
- ΔEVE ≈ −D_A × A × Δy + D_L × L × Δy with duration-gap decomposition
- Full repricing gap table across 11 buckets
- 7 standard scenarios + custom scenario definition
- Risk copilot with LLM narrative and fallback

### VolLab — Quant Math Rigor
- Black-Scholes: C = SN(d₁) − Ke^{−rT}N(d₂), closed-form + IV solver
- Greeks: analytical and finite-difference with convergence tests
- Monte Carlo with antithetic variates, verified convergence to BS within 1%
- Vol surface with skew/smile + bilinear spline interpolation

### RegimeOS — Agentic Orchestration + Probabilistic Reasoning
- p(z_t = k | x_t) via softmax over regime prototypes
- Transition detection with driver attribution
- Regime-to-action playbooks, HITL approval queue
- Explainer agent with LLM narrative + structured fallback

---

## Shared Engineering Standards

Every project in this suite has:

- Clean Python package with `pyproject.toml` and `pip install -e .`
- Typed Pydantic models for all data contracts
- FastAPI with structured JSON responses and `/health` endpoint
- CLI via Typer (each project has ≥5 commands)
- pytest test suite (26–35 tests per project, all passing)
- Local demo path — no cloud required
- README with business case, math, architecture, limitations, and production path

---

## Quick Start (any project)

```bash
# Clone this repo, then enter any project
cd atlas       # or fedlens / balancelab / vollab / regimeos
pip install -e ".[dev]"
make test
make serve
```

---

## Technology Signals

| Signal | Where |
|---|---|
| Python · polars · DuckDB · parquet | Atlas, BalanceLab, RegimeOS |
| FAISS · sentence-transformers · embeddings | FedLens |
| FastAPI · Pydantic v2 · Typer | All five |
| NumPy · SciPy · Monte Carlo | VolLab |
| LLM-agentic workflows · RAG · HITL | FedLens, BalanceLab, RegimeOS |
| Event studies · abnormal returns | FedLens |
| Black-Scholes · Greeks · IV solver | VolLab |
| NII / EVE / ALM / deposit beta | BalanceLab |
| Regime detection · probabilistic state | RegimeOS |
| scikit-learn · feature pipelines | Atlas, RegimeOS |

---

## About

Built as a portfolio demonstrating enterprise AI and financial analytics capabilities across macro data systems, policy-language intelligence, balance-sheet risk, derivatives math, and decision-support orchestration.

Each project is designed to be: technically correct, honest about its assumptions, and production-path-aware. The math is visible. The limitations are documented. The AI is real, not decorative.
