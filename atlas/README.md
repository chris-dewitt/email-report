# Atlas

**Macro intelligence platform for economic state tracking, feature engineering, and executive-quality monitoring.**

---

## Business Case

A strategy or treasury team needs one trustworthy macro data backbone: pull from many sources, standardize frequencies, build thematic indicators, and expose a clean API for monitoring the economic regime. Atlas is that backbone — and the data foundation that feeds RegimeOS.

---

## What It Does

| Capability | Description |
|---|---|
| Data ingestion | 36 curated series from FRED (32) and yfinance (4) across 6 themes |
| Feature engineering | 100+ features: z-scores, YoY changes, rolling windows, log-diffs, percentile ranks |
| Regime classification | Rules-based macro regime (expansion, overheating, slowdown, contraction, stress) |
| Bronze/silver/gold | Layered parquet pipeline with calendar alignment and transform separation |
| FastAPI serving | REST endpoints for series, feature groups, regime snapshots |
| DuckDB analytics | Embedded OLAP — query gold layer with SQL |
| Macro copilot | LLM-powered weekly briefing, cites specific series and features (Ollama) |

---

## Themes and Series

| Theme | Example Series |
|---|---|
| Inflation | CPI, PCE, Core CPI, 5Y Inflation Expectations |
| Labor | Unemployment, Payrolls, JOLTS, Labor Force Participation |
| Rates | Fed Funds, DGS2, DGS10, Yield Curve Spread |
| Financial Conditions | Spreads, VIX proxy, Dollar Index |
| Growth | GDP, Industrial Production, Retail Sales |
| FX / Market | SPY, DXY, USDEUR, USDGBP |

---

## Key Mathematics

**Z-score standardization**
```
z_t = (x_t − μ_t) / σ_t
```
where μ_t and σ_t are rolling window means and standard deviations.

**Year-over-year change**
```
yoy_t = (x_t − x_{t−52}) / x_{t−52}   [weekly]
       = (x_t − x_{t−12}) / x_{t−12}   [monthly]
```

**Optional PCA factor view:** inflation, labor, and financial-conditions blocks reduced to latent signals for regime detection input.

---

## Architecture

```
FRED API + yfinance
    └─► Bronze layer (raw parquet, one file per series)
            └─► Silver layer (calendar-aligned, transformed)
                    └─► Gold layer (themed feature blocks, regime snapshots)
                                ├─► FastAPI (/series, /feature-groups, /regime-snapshot)
                                ├─► DuckDB (SQL analytical queries)
                                └─► Copilot (Ollama briefing, citation extraction)
```

**Stack:** Python · polars · DuckDB · FastAPI · Typer · fredapi · yfinance · (Ollama optional)

---

## Local Setup

```bash
git clone <repo>
cd atlas
pip install -e ".[dev]"

# Initialize and pull data (requires FRED API key)
export FRED_API_KEY=your_key_here
atlas init
atlas pull
atlas build-features
atlas snapshot

# Start API
atlas serve
# → http://localhost:8000/docs

# Generate macro briefing
atlas copilot "What changed in inflation this week?"
```

**No cloud required.** All data stored in local parquet files; DuckDB for queries.

---

## CLI Reference

| Command | Description |
|---|---|
| `atlas init` | Initialize data directories and DuckDB |
| `atlas pull` | Ingest from FRED and yfinance |
| `atlas build-features` | Run bronze → silver → gold pipeline |
| `atlas snapshot` | Compute regime classification |
| `atlas status` | Data freshness dashboard |
| `atlas export-report` | Export gold layer to CSV/JSON |
| `atlas copilot` | Run macro briefing via Ollama |
| `atlas serve` | Start FastAPI on port 8000 |

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `/health` | System status and data quality |
| `/series` | List all series with metadata |
| `/series/{id}/history` | Full history with date range filters |
| `/feature-groups` | Themed feature groups with latest z-scores |
| `/regime-snapshot` | Current regime + confidence + key drivers |
| `/copilot` | LLM-generated macro briefing |

---

## Test Suite

```bash
pytest -v
```

Tests cover: registry catalog integrity (36 series, 6 themes), feature transform correctness (z-score, YoY, rolling, log-diff), API health endpoint, and data quality assertions.

---

## Cross-Project Integration

Atlas is the data backbone for **RegimeOS**. The `atlas export-report` command produces macro feature z-scores that RegimeOS consumes via `signals.builder.build_signal_vector`. This creates a shared macro layer rather than duplicate data logic across repos.

---

## Limitations and Future Work

- Requires a FRED API key (free from fred.stlouisfed.org)
- Calendar alignment is approximate for mixed-frequency series
- No vintage tracking (uses current revisions only)
- PCA factor view is available but not wired to the main dashboard yet
- Nowcasting module is a stretch goal
