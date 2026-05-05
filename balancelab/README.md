# BalanceLab

**ALM, NII, EVE, liquidity-gap, and scenario analytics platform with an internal risk copilot.**

---

## Business Case

Treasury and balance-sheet risk teams need a clear, auditable way to run rate scenarios and explain what they mean for earnings and economic value. BalanceLab provides a structured platform for uploading positions, running standard and custom rate shocks, and generating plain-language narratives suitable for ALCO presentations.

---

## What It Does

| Capability | Description |
|---|---|
| Position ingestion | Upload a balance sheet as JSON; maps to standardized repricing/maturity profile |
| Scenario engine | 7 standard scenarios (±100/200 bps parallel, steepener, flattener) + custom |
| NII sensitivity | Δ NII ≈ Σ (RSA_i − RSL_i) × Δr_i × horizon, with deposit-beta adjustments |
| EVE sensitivity | Δ EVE ≈ −D_A × A × Δy + D_L × L × Δy, using duration-bucket approximations |
| Liquidity gap table | Repricing gap by bucket, cumulative gap, and 1-year gap ratio |
| Risk copilot | LLM-powered narrative explaining what the results mean (Ollama, with fallback) |
| HITL governance | Scenarios and narratives require explicit approval before export |

---

## Key Mathematics

**NII Sensitivity**
```
ΔNII ≈ Σᵢ (RSAᵢ − RSLᵢ) × Δrᵢ × (horizon / 12)
```
where RSA_i and RSL_i are rate-sensitive assets and liabilities in bucket i, and deposit betas dampen the liability repricing: `Δr_liability = β × Δr`.

**EVE Sensitivity**
```
ΔEVE ≈ −D_A × A × Δy + D_L × L × Δy
```
where D_A and D_L are weighted-average modified durations. Duration gap = D_A − D_L; a positive gap loses EVE when rates rise.

> **Stylization note**: Durations are bucket-midpoint approximations. Production ALM systems use full cash-flow engines with prepayment models. This is a portfolio demo, not a regulatory submission.

---

## Architecture

```
JSON upload
    └─► Input layer (position parsing, product mapping)
            └─► Analytics layer (NII, EVE, gap, FTP)
                    └─► API layer (FastAPI, /nii, /eve, /liquidity-gap, /shock)
                            └─► Copilot layer (Ollama-backed narrative + fallback)
                                    └─► Governance layer (approval queue, export pack)
```

**Stack:** Python · FastAPI · Pydantic · Polars · DuckDB · Typer · (Ollama optional)

---

## Local Setup

```bash
git clone <repo>
cd balancelab
pip install -e ".[dev]"

# Load the sample balance sheet and run all scenarios
balancelab shock sample_data/sample_balance_sheet.json --scenario up_200
balancelab export-pack sample_data/sample_balance_sheet.json

# Start the API
balancelab serve
# → http://localhost:8001/docs
```

No cloud required. DuckDB is the local analytical store; no Postgres or external services needed for the core demo.

---

## CLI Reference

| Command | Description |
|---|---|
| `balancelab init` | Initialize data directories |
| `balancelab load <path>` | Preview a balance-sheet file |
| `balancelab map-products <path>` | Show repricing profile |
| `balancelab shock <path> --scenario up_200` | Run a rate scenario |
| `balancelab export-pack <path>` | Run all scenarios, export JSON |
| `balancelab serve` | Start FastAPI on port 8001 |

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | System status |
| `/positions` | GET / POST | Balance sheet summary / upload |
| `/scenarios` | GET / POST | List or create scenarios |
| `/shock/{scenario_id}` | GET | Full scenario output (NII + EVE + gap) |
| `/nii/{scenario_id}` | GET | NII only |
| `/eve/{scenario_id}` | GET | EVE only |
| `/liquidity-gap` | GET | Gap table |
| `/shock-all` | GET | All scenarios in one call |
| `/copilot` | POST | LLM-generated risk narrative |

---

## Test Suite

```bash
pytest -v   # 26 tests
```

Tests cover: NII mechanics, deposit-beta dampening, EVE duration-gap direction, gap table accounting, catalog management, API smoke tests, and copilot fallback narrative.

---

## Limitations and Future Work

- Duration approximations use bucket midpoints; production would require full cash-flow discounting
- Deposit behavior is modeled with static betas; dynamic balance migration and optionality are stretch goals
- The copilot requires Ollama running locally; enterprise deployments would use an internal LLM endpoint
- No FTP curve management or hedge overlay in the current build
- Multi-currency positions not supported

---

## Production Path

A production pilot would add: full cash-flow engine with prepayment assumptions, behavioral deposit models (beta estimation from historical data), FHLB and wholesale funding integration, regulatory capital impact views, and integration with the core banking system position feed.
