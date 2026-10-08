from fastapi import APIRouter
from app.routers.market import router as market_router
from app.routers.radar import router as radar_router
from app.routers.closing_bet import router as closing_bet_router

api_router = APIRouter()

api_router.include_router(market_router)
api_router.include_router(radar_router)
api_router.include_router(closing_bet_router)

__all__ = ["api_router"]