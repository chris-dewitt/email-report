"""Pydantic settings for FedLens."""

from __future__ import annotations

from pydantic import BaseModel


class OllamaSettings(BaseModel):
    host: str = "http://localhost:11434"
    model: str = "mistral"
    timeout_seconds: int = 300


class EmbeddingSettings(BaseModel):
    model_name: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    batch_size: int = 32
    device: str = "cpu"


class APISettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8001
    cors_origins: list[str] = [
        "http://localhost:5174",
        "http://localhost:3000",
    ]


class EventStudySettings(BaseModel):
    pre_window_days: int = 2
    post_window_days: int = 5
    estimation_window_days: int = 120
    gap_days: int = 10
    benchmark_model: str = "constant_mean"
    history_start: str = "2010-01-01"


class IngestSettings(BaseModel):
    fed_base_url: str = "https://www.federalreserve.gov"
    scrape_delay_seconds: float = 1.5
    start_year: int = 2010
    chunk_size_tokens: int = 512
    chunk_overlap_tokens: int = 64


class FedLensSettings(BaseModel):
    """Root settings object for FedLens."""

    data_dir: str = "./data"
    ollama: OllamaSettings = OllamaSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    api: APISettings = APISettings()
    event_study: EventStudySettings = EventStudySettings()
    ingest: IngestSettings = IngestSettings()
