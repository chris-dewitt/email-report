# FedLens

**Fed communication intelligence engine — linking policy language to rates, equities, and volatility moves.**

---

## Business Case

MDs and strategy teams track Fed language carefully, but reading every FOMC statement, minutes release, and speech manually is slow and inconsistent. FedLens turns the full corpus of Fed communications into a searchable, evaluated copilot with event-study evidence — so "what did the Fed's tone shift mean for 2-year yields?" has a data-backed answer in seconds.

---

## What It Does

| Capability | Description |
|---|---|
| Document corpus | 59+ FOMC statements (2020–2026), with minutes and speech support |
| NLP pipeline | Hawkish/dovish scoring (40+ curated terms), uncertainty, topic classification |
| Semantic embeddings | sentence-transformers (all-MiniLM-L6-v2), FAISS vector store |
| Semantic drift | Cosine-similarity drift between consecutive documents; rolling 4-meeting average |
| Event studies | Abnormal returns: AR_t = R_t − E[R_t] across windows around document timestamps |
| Research copilot | RAG-based briefing agent with citation of specific text chunks and market windows |
| HITL review queue | All briefings are "pending" until analyst approves or rejects |

---

## Key Mathematics

**Abnormal return (event study)**
```
AR_t = R_t − E[R_t]
CAR = Σ AR_t  over [t₁, t₂]
```
where E[R_t] is the market's expected return (historical mean over the estimation window).

**Semantic drift**
```
drift_t = 1 − cos(embed(doc_t), embed(doc_{t−1}))
```
where embeddings are document-level averages of chunk embeddings.

**Hawkish/dovish score**
```
net_score = (hawkish_hits − dovish_hits) / total_hits
confidence = total_hits / chunk_length
```

---

## Architecture

```
FOMC.gov / Fed speeches
    └─► Ingest (scraper, parser, chunker) → Bronze (HTML + JSON)
            └─► Model layer (sentiment, embeddings, drift, uncertainty) → Silver/Gold
                    ├─► FAISS vector store (semantic search)
                    ├─► DuckDB (SQL over metadata + features)
                    └─► Copilot (RAG → Ollama → HITL review queue)
```

**Stack:** Python · sentence-transformers · FAISS · FastAPI · Pydantic · Typer · Ollama (optional)

---

## Local Setup

```bash
git clone <repo>
cd fedlens
pip install -e ".[dev]"

# Data is already seeded (59 statements in data/bronze/statement/)
fedlens init

# Build the NLP pipeline
fedlens embed      # generate embeddings
fedlens analyze    # sentiment + drift + uncertainty

# Run event studies
fedlens event-study --series DGS2 DGS10 SPY

# Generate a briefing
fedlens brief "How did the Fed's tone change during the 2022 hiking cycle?"

# Start API
fedlens serve
# → http://localhost:8000/docs (FedLens runs on same port as Atlas by default)
```

---

## CLI Reference

| Command | Description |
|---|---|
| `fedlens init` | Initialize data directories |
| `fedlens ingest` | Scrape and parse Fed documents |
| `fedlens embed` | Generate chunk embeddings |
| `fedlens analyze` | Sentiment, drift, uncertainty features |
| `fedlens event-study` | Run abnormal return analysis |
| `fedlens brief` | RAG-powered briefing via Ollama |
| `fedlens serve` | Start FastAPI |
| `fedlens status` | Data freshness |

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/documents` | GET | List documents with optional sentiment join |
| `/documents/{id}` | GET | Chunks for a specific document |
| `/search` | POST | Semantic search (query + date filters) |
| `/event-study` | GET | Event study results |
| `/event-study/{doc_id}` | GET | Event study for a specific document |
| `/briefing` | POST | RAG-powered Q&A |
| `/reviews` | GET | HITL review queue |
| `/reviews/approve/{id}` | POST | Approve a briefing |
| `/reviews/reject/{id}` | POST | Reject a briefing |
| `/sentiment` | GET | Sentiment time series |
| `/drift` | GET | Semantic drift time series |

---

## Test Suite

```bash
pytest -v
```

Coverage: document parsing, chunk integrity, embedding shapes, event study abnormal return math, briefing citation extraction, API endpoints.

---

## Cross-Project Integration

FedLens exports `policy_sentiment` scores into **RegimeOS** via the `SignalVector.policy_sentiment` field. This connects the Fed's tone directly to regime classification — overheating regimes are more likely when sentiment is hawkish and inflation signals are elevated simultaneously.

---

## Limitations and Future Work

- Minutes and speech ingestion is implemented but not seeded — only statements are in the corpus by default
- Sentiment is dictionary-based; LLM-based tone classification is a stretch goal
- Multi-document comparison mode (across meetings) is wired but not exposed in the main UI
- No speaker-level fingerprinting yet (Powell vs. Brainard hawkishness decomposition)
- Continuous evaluation dashboard for briefing quality is a stretch goal
