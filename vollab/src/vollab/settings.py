from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_port: int = 8002
    mc_default_paths: int = 100_000
    mc_default_seed: int = 42

    model_config = {"env_prefix": "VOLLAB_"}


settings = Settings()
