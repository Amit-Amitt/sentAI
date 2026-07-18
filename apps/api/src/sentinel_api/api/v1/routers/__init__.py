from fastapi import APIRouter

from sentinel_api.api.v1.routers.agents import router as agents_router
from sentinel_api.api.v1.routers.coordinator import router as coordinator_router
from sentinel_api.api.v1.routers.health import router as health_router
from sentinel_api.api.v1.routers.incidents import router as incidents_router
from sentinel_api.api.v1.routers.reports import router as reports_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(incidents_router)
api_router.include_router(coordinator_router)
api_router.include_router(agents_router)
api_router.include_router(reports_router)
