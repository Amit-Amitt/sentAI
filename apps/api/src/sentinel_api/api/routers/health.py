from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str = Field("healthy", description="Application health status indicator")
    version: str = Field("1.0.0", description="Backend service version")


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Liveness check endpoint.

    Returns a positive health indicator and current application version.
    """
    return HealthResponse(status="healthy", version="1.0.0")
