from fastapi import APIRouter
from app.core.config import RouteConfig
from app.services.market_service import (
    get_volume_top50_data,
    get_market_indicators_top10_data,
)

router = APIRouter(
    prefix=RouteConfig.MARKET_PREFIX,
    tags=RouteConfig.MARKET_TAGS
)

@router.get("/volume-top50")
def get_volume_top50():
    return get_volume_top50_data()

@router.get("/indicators-top10")
def get_market_indicators_top10():
    return get_market_indicators_top10_data()