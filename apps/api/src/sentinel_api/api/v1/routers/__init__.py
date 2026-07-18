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
from sentinel_api.api.v1.routers.simulation import router as simulation_router
from sentinel_api.api.v1.routers.remediation import router as remediation_router
from sentinel_api.api.v1.routers.telemetry import router as telemetry_router
from sentinel_api.api.v1.routers.stream import router as stream_router
from sentinel_api.api.v1.routers.otlp import router as otlp_router
from sentinel_api.api.v1.routers.github import router as github_router
from sentinel_api.api.v1.routers.observability import router as observability_router
from sentinel_api.api.v1.routers.remediation import router as remediation_router
from sentinel_api.api.v1.routers.collaboration import router as collaboration_router
from sentinel_api.api.v1.routers.auth import router as auth_router
from sentinel_api.api.v1.routers.iam import router as iam_router
from sentinel_api.api.v1.routers.billing import router as billing_router
from sentinel_api.api.v1.routers.demo import router as demo_router

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
api_router.include_router(simulation_router)
api_router.include_router(remediation_router)
api_router.include_router(telemetry_router)
api_router.include_router(stream_router)
api_router.include_router(otlp_router)
api_router.include_router(github_router)
api_router.include_router(observability_router)
api_router.include_router(remediation_router)
api_router.include_router(collaboration_router)
api_router.include_router(auth_router)
api_router.include_router(iam_router)
api_router.include_router(billing_router)
api_router.include_router(demo_router)


