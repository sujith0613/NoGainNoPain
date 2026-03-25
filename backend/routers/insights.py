"""
Routers: insights.py — handles all market intelligence endpoints.
"""
from fastapi import APIRouter, Query
from decision_engine.business_recommendation import get_business_recommendation
from decision_engine.pricing_engine import get_pricing_analysis
from decision_engine.menu_generator import get_menu_recommendations
from decision_engine.demand_supply import get_demand_gap
from decision_engine.trend_engine import get_trend_analysis
from decision_engine.sentiment_engine import get_sentiment_analysis
from decision_engine.peak_hour_analyzer import get_peak_hours
from decision_engine.combo_engine import get_combo_analysis
from decision_engine.scenario_simulator import simulate_scenario
from decision_engine.heatmap import get_heatmap_data

router = APIRouter(prefix="/api", tags=["Market Intelligence"])


@router.get("/business-recommendation")
async def business_recommendation(
    area: str = Query(..., description="Target area"),
    budget: float = Query(..., description="Budget in INR"),
    city: str = Query("", description="City (optional)"),
):
    return get_business_recommendation(area=area, budget=budget, city=city)


@router.get("/pricing-analysis")
async def pricing_analysis(
    area: str = Query(...),
    cuisine_type: str = Query(...),
):
    return get_pricing_analysis(area=area, cuisine_type=cuisine_type)


@router.get("/menu-generation")
async def menu_generation(
    area: str = Query(...),
    cuisine_type: str = Query(...),
    top_n: int = Query(10),
):
    return get_menu_recommendations(area=area, cuisine_type=cuisine_type, top_n=top_n)


@router.get("/demand-gap")
async def demand_gap(
    city: str = Query(""),
    area: str = Query(""),
):
    return get_demand_gap(city=city, area=area)


@router.get("/trend-analysis")
async def trend_analysis(
    city: str = Query(""),
    cuisine_type: str = Query(""),
):
    return get_trend_analysis(city=city, cuisine_type=cuisine_type)


@router.get("/sentiment-analysis")
async def sentiment_analysis(
    area: str = Query(""),
    cuisine_type: str = Query(""),
):
    return get_sentiment_analysis(area=area, cuisine_type=cuisine_type)


@router.get("/peak-hours")
async def peak_hours(
    area: str = Query(""),
    cuisine_type: str = Query(""),
):
    return get_peak_hours(area=area, cuisine_type=cuisine_type)


@router.get("/combo-analysis")
async def combo_analysis(
    cuisine_type: str = Query(""),
    area: str = Query(""),
):
    return get_combo_analysis(cuisine_type=cuisine_type, area=area)


@router.get("/scenario-simulation")
async def scenario_simulation(
    area: str = Query(...),
    cuisine_type: str = Query(...),
    budget: float = Query(...),
):
    return simulate_scenario(area=area, cuisine_type=cuisine_type, budget=budget)


@router.get("/heatmap-data")
async def heatmap_data(
    city: str = Query(""),
):
    return get_heatmap_data(city=city)


# ── Metadata endpoints ─────────────────────────────────────────────────────────
@router.get("/areas")
async def list_areas(city: str = Query("")):
    from data_pipeline.ingestion import load_raw_data
    df = load_raw_data({"city": city} if city else {})
    if df.empty:
        return {"areas": []}
    areas = sorted(df["area"].dropna().unique().tolist())
    return {"areas": areas}


@router.get("/cities")
async def list_cities():
    from data_pipeline.ingestion import load_raw_data
    df = load_raw_data()
    if df.empty:
        return {"cities": []}
    return {"cities": sorted(df["city"].dropna().unique().tolist())}


@router.get("/cuisines")
async def list_cuisines():
    from data_pipeline.ingestion import load_raw_data
    df = load_raw_data()
    if df.empty:
        return {"cuisines": []}
    return {"cuisines": sorted(df["cuisine_type"].dropna().unique().tolist())}


@router.get("/restaurants")
async def list_restaurants(area: str = Query(""), city: str = Query("")):
    from data_pipeline.ingestion import load_raw_data
    filters = {}
    if city:
        filters["city"] = city
    df = load_raw_data(filters)
    if df.empty:
        return {"restaurants": []}
    if area:
        df = df[df["area"].str.lower() == area.lower()]
    rests = (
        df[["restaurant_id", "restaurant_name", "area", "city", "cuisine_type"]]
        .drop_duplicates(subset=["restaurant_id"])
        .to_dict(orient="records")
    )
    return {"restaurants": rests}
