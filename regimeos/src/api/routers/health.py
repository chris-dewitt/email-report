from fastapi import APIRouter
from pydantic import BaseModel
from regimeos import __version__
from regimeos.models.regime import RegimeLabel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    regime_labels: list[str]


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        version=__version__,
        regime_labels=[r.value for r in RegimeLabel],
    )
