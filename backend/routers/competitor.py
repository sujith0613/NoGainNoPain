"""
Routers: competitor.py — handles competitor analysis endpoints.
"""
from fastapi import APIRouter, Query
from decision_engine.competitor_analysis import (
    get_competitor_analysis,
    get_performance_score,
    get_improvement_recommendations,
    get_gap_analysis,
)

router = APIRouter(prefix="/api", tags=["Competitor Intelligence"])


@router.get("/competitor-analysis")
async def competitor_analysis(
    restaurant_name: str = Query(""),
    restaurant_id: str = Query(""),
    area: str = Query(""),
    cuisine_type: str = Query(""),
):
    return get_competitor_analysis(
        restaurant_name=restaurant_name,
        restaurant_id=restaurant_id,
        area=area,
        cuisine_type=cuisine_type,
    )


@router.get("/performance-score")
async def performance_score(
    restaurant_name: str = Query(""),
    restaurant_id: str = Query(""),
):
    return get_performance_score(
        restaurant_name=restaurant_name,
        restaurant_id=restaurant_id,
    )


@router.get("/improvement-recommendations")
async def improvement_recommendations(
    restaurant_name: str = Query(""),
    restaurant_id: str = Query(""),
):
    return get_improvement_recommendations(
        restaurant_name=restaurant_name,
        restaurant_id=restaurant_id,
    )


@router.get("/gap-analysis")
async def gap_analysis(
    restaurant_name: str = Query(""),
    restaurant_id: str = Query(""),
):
    return get_gap_analysis(
        restaurant_name=restaurant_name,
        restaurant_id=restaurant_id,
    )
