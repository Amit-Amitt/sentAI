from fastapi import APIRouter, Depends

from sentinel_api.api.v1.controllers.coordinator import WorkflowController
from sentinel_api.api.v1.validators.schemas import CoordinatorRunRequest

router = APIRouter(prefix="/coordinator", tags=["coordinator"])


def get_controller() -> WorkflowController:
    """Dependency helper instantiating WorkflowController."""
    return WorkflowController()


@router.post("/run", response_model=dict)
async def run_workflow(
    payload: CoordinatorRunRequest,
    controller: WorkflowController = Depends(get_controller),
) -> dict:
    """Invokes the LangGraph multi-agent execution pipeline."""
    return await controller.run(payload)

@router.get("/{thread_id}/status", response_model=dict)
async def get_workflow_status(
    thread_id: str,
    controller: WorkflowController = Depends(get_controller),
) -> dict:
    """Fetches the live status and execution timeline of a workflow run."""
    return await controller.get_status(thread_id)
