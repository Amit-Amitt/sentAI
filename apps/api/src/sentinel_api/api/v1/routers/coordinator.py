from fastapi import APIRouter, Depends

from sentinel_api.api.v1.controllers.coordinator import CoordinatorController
from sentinel_api.api.v1.validators.schemas import CoordinatorRunRequest

router = APIRouter(prefix="/coordinator", tags=["coordinator"])


def get_controller() -> CoordinatorController:
    """Dependency helper instantiating CoordinatorController."""
    return CoordinatorController()


@router.post("/run", response_model=dict)
async def run_coordinator(
    payload: CoordinatorRunRequest,
    controller: CoordinatorController = Depends(get_controller),
) -> dict:
    """Manually invokes the coordinator multi-agent execution pipeline."""
    return await controller.run(payload)
