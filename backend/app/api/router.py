from fastapi import APIRouter

from app.api.routes import ai, auth, businesses, health, intelligence, records, reports

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(ai.router)
api_router.include_router(businesses.router, tags=["businesses"])
api_router.include_router(records.router, tags=["records"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(intelligence.router)
