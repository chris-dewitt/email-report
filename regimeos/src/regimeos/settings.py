from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    data_dir: Path = Path("./data")
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    api_port: int = 8003
    duckdb_path: str = "regimeos.duckdb"

    model_config = {"env_prefix": "REGIMEOS_"}


settings = Settings()
