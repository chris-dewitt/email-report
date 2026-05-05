from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    positions_loaded: int = 0
    scenarios_available: int = 0
    data_dir_exists: bool = False
