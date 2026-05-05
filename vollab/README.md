# VolLab

**Derivatives pricing, Greeks, volatility-surface, and stochastic-simulation lab.**

---

## Business Case

Quant managers and risk teams need a reference implementation that bridges theory and practice: one place to price options, inspect Greeks, explore vol surface structure, and run scenario PnL — with the mathematics explicitly documented. VolLab is that lab.

---

## What It Does

| Capability | Description |
|---|---|
| Black-Scholes pricing | Analytical European call/put pricing with put-call parity checks |
| Monte Carlo | Risk-neutral GBM simulation with antithetic variates and convergence tracking |
| Implied volatility | Newton-Raphson solver — round-trips within 1e-6 |
| Greeks (analytical) | Delta, Gamma, Theta, Vega, Rho — closed-form BSM |
| Greeks (finite-diff) | Independent finite-difference check against any pricing function |
| Vol surface | Stylized equity surface with skew/smile; bilinear spline interpolation |
| Scenario PnL | Spot × vol stress grid — 45 scenarios in one call |
| GBM simulation | Discretized path simulation for research and pricing |

---

## Key Mathematics

**Underlying dynamics (risk-neutral measure)**
```
dS_t = r S_t dt + σ S_t dW_t
```

**European call price (Black-Scholes-Merton)**
```
C = S·e^{−qT}·N(d₁) − K·e^{−rT}·N(d₂)

d₁ = [ln(S/K) + (r − q + σ²/2)T] / (σ√T)
d₂ = d₁ − σ√T
```

**Put-call parity**
```
C − P = S·e^{−qT} − K·e^{−rT}
```

**Monte Carlo (antithetic variates)**
```
S_T = S₀ · exp[(r − q − σ²/2)T + σ√T · Z],  Z ~ N(0,1)
Price = e^{−rT} · E[max(S_T − K, 0)]
```

**Greeks (selected)**
```
Δ = e^{−qT} N(d₁)           [call delta]
Γ = e^{−qT} φ(d₁) / (S σ √T)
ν = S e^{−qT} φ(d₁) √T / 100
```

> **When do BS assumptions fail?** Constant volatility, no jumps, continuous trading, no transaction costs. Implied vol skew is direct evidence of violation — the surface module demonstrates this.

---

## Architecture

```
OptionContract (Pydantic)
    ├─► pricing/black_scholes.py   — analytical pricing + implied vol
    ├─► pricing/monte_carlo.py     — GBM simulation pricing
    ├─► greeks/analytical.py       — closed-form Greeks
    ├─► greeks/finite_diff.py      — numerical Greek check
    ├─► surface/builder.py         — vol surface + spline interpolation
    └─► simulation/scenario.py     — spot×vol PnL grid
```

**Stack:** Python · NumPy · SciPy · FastAPI · Pydantic · Typer

---

## Local Setup

```bash
git clone <repo>
cd vollab
pip install -e ".[dev]"

# Price an ATM call
vollab price --spot 100 --strike 100 --expiry 1.0 --vol 0.20 --rate 0.05

# Greeks (analytical vs finite-difference comparison)
vollab greeks --spot 100 --strike 100 --expiry 1.0 --vol 0.20 --rate 0.05

# Vol surface
vollab surface

# Stress PnL grid
vollab stress --spot 100 --strike 100 --expiry 1.0 --vol 0.20 --rate 0.05

# Benchmark BS vs MC
vollab benchmark --n-paths 500000

# Start API
vollab serve
# → http://localhost:8002/docs
```

---

## CLI Reference

| Command | Description |
|---|---|
| `vollab price` | BS + MC pricing, intrinsic, time value |
| `vollab greeks` | Analytical vs finite-difference Greeks table |
| `vollab surface` | Print vol surface grid |
| `vollab stress` | Spot × vol PnL matrix |
| `vollab benchmark` | BS vs MC timing comparison |
| `vollab serve` | Start FastAPI on port 8002 |

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Methods available |
| `/price/bs` | POST | Black-Scholes price |
| `/price/mc` | POST | Monte Carlo price |
| `/price/compare` | POST | Both methods side-by-side |
| `/greeks/analytical` | POST | Closed-form Greeks |
| `/greeks/fd` | POST | Finite-difference Greeks |
| `/greeks/compare` | POST | Both methods |
| `/surface/sample` | GET | Full vol surface |
| `/surface/interpolate` | GET | Point interpolation |
| `/scenario-pnl` | POST | Spot × vol stress grid |

---

## Test Suite

```bash
pytest -v   # 35 tests
```

Tests cover: put-call parity, implied vol round-trip, deep ITM/OTM boundary conditions, MC convergence to BS, antithetic variance reduction, analytical vs FD Greek consistency, vol surface skew direction, interpolation accuracy.

---

## Limitations and Future Work

- European options only (no American exercise, no early exercise modeling)
- Single-asset GBM only (no jump-diffusion, no stochastic vol, no local vol)
- Vol surface is stylized, not calibrated to real market quotes
- No term structure of interest rates
- Stretch goals: Heston model, local vol calibration, rates/FX extensions, Julia/C++ kernel benchmarks

---

## Production Path

Production derivatives pricing systems add: full term structure calibration, jump-diffusion or stochastic-vol models, Monte Carlo with variance reduction suites, closed-form approximations for exotics, C++ pricing kernels for latency-sensitive paths, and integration with market data feeds for real-time surface construction.
