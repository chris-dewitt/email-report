from fastapi import FastAPI
from api.routers import health, signals, state, recommendations, approval

app = FastAPI(
    title="RegimeOS API",
    version="0.1.0",
    description="Regime detection and decision-support orchestration",
)

app.include_router(health.router, tags=["health"])
app.include_router(signals.router, prefix="/signals", tags=["signals"])
app.include_router(state.router, prefix="/state", tags=["state"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(approval.router, prefix="/approval-queue", tags=["approval"])
