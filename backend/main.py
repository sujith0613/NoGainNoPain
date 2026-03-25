"""
Main FastAPI application entry point.
Seeds MongoDB on startup, registers all routers.
"""
import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Seed database on startup."""
    try:
        from data.seed_data import seed_database
        seed_database()
    except Exception as e:
        print(f"[startup] Seed warning: {e}")
    yield


app = FastAPI(
    title="Food Market Intelligence & Decision Engine",
    description="AI-powered food market intelligence system for business decision-making",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from routers.insights import router as insights_router
from routers.competitor import router as competitor_router

app.include_router(insights_router)
app.include_router(competitor_router)


@app.get("/")
async def root():
    return {
        "service": "Food Market Intelligence & Decision Engine",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "/api/business-recommendation",
            "/api/pricing-analysis",
            "/api/menu-generation",
            "/api/demand-gap",
            "/api/trend-analysis",
            "/api/sentiment-analysis",
            "/api/peak-hours",
            "/api/combo-analysis",
            "/api/scenario-simulation",
            "/api/heatmap-data",
            "/api/competitor-analysis",
            "/api/performance-score",
            "/api/improvement-recommendations",
            "/api/gap-analysis",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
