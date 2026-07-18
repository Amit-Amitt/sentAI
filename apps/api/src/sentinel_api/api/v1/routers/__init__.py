from fastapi import APIRouter

from sentinel_api.api.v1.routers.agents import router as agents_router
from sentinel_api.api.v1.routers.coordinator import router as coordinator_router
from sentinel_api.api.v1.routers.health import router as health_router
from sentinel_api.api.v1.routers.incidents import router as incidents_router
from sentinel_api.api.v1.routers.invitations import router as invitations_router
from sentinel_api.api.v1.routers.organizations import router as organizations_router
from sentinel_api.api.v1.routers.reports import router as reports_router
from sentinel_api.api.v1.routers.workspaces import router as workspaces_router
from sentinel_api.api.v1.routers.api_keys import router as api_keys_router
from sentinel_api.api.v1.routers.integrations import router as integrations_router
from sentinel_api.api.v1.routers.memory import router as memory_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(incidents_router)
api_router.include_router(coordinator_router)
api_router.include_router(agents_router)
api_router.include_router(reports_router)
api_router.include_router(organizations_router)
api_router.include_router(workspaces_router)
api_router.include_router(invitations_router)
api_router.include_router(api_keys_router)
api_router.include_router(integrations_router)
api_router.include_router(memory_router)


