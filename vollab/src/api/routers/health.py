from fastapi import APIRouter
from pydantic import BaseModel

from vollab import __version__

router = APIRouter()


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    methods: list[str]


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        version=__version__,
        methods=["black_scholes", "monte_carlo", "finite_difference"],
    )
