from fastapi import FastAPI
from api.routers import health, positions, scenarios, analysis, copilot

app = FastAPI(
    title="BalanceLab API",
    version="0.1.0",
    description="ALM, NII, EVE, liquidity-gap, and scenario analytics",
)

app.include_router(health.router, tags=["health"])
app.include_router(positions.router, prefix="/positions", tags=["positions"])
app.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
app.include_router(analysis.router, tags=["analysis"])
app.include_router(copilot.router, prefix="/copilot", tags=["copilot"])
