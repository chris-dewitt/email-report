from fastapi import FastAPI
from api.routers import health, pricing, greeks, surface, scenario

app = FastAPI(
    title="VolLab API",
    version="0.1.0",
    description="Derivatives pricing, Greeks, volatility surfaces, and scenario PnL",
)

app.include_router(health.router, tags=["health"])
app.include_router(pricing.router, prefix="/price", tags=["pricing"])
app.include_router(greeks.router, prefix="/greeks", tags=["greeks"])
app.include_router(surface.router, prefix="/surface", tags=["surface"])
app.include_router(scenario.router, prefix="/scenario-pnl", tags=["scenario"])
