from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    data_dir: Path = Path("./data")
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    api_port: int = 8001
    duckdb_path: str = "balancelab.duckdb"

    model_config = {"env_prefix": "BALANCELAB_"}


settings = Settings()
