from fastapi import APIRouter

from balancelab import __version__
from balancelab.config import DATA_DIR
from balancelab.models.health import HealthResponse
from balancelab.models.scenarios import STANDARD_SCENARIOS

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        version=__version__,
        scenarios_available=len(STANDARD_SCENARIOS),
        data_dir_exists=DATA_DIR.exists(),
    )
