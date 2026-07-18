from fastapi import APIRouter, Depends

from sentinel_api.api.v1.controllers.agents import AgentsController
from sentinel_api.api.v1.validators.schemas import AgentRunRequest

router = APIRouter(prefix="/agents", tags=["agents"])


def get_controller() -> AgentsController:
    """Dependency helper instantiating AgentsController."""
    return AgentsController()


@router.post("/log", response_model=dict)
async def run_log_agent(
    payload: AgentRunRequest,
    controller: AgentsController = Depends(get_controller),
) -> dict:
    """Executes the Log Agent independently and returns findings."""
    return await controller.run_agent("log", payload)


@router.post("/metrics", response_model=dict)
async def run_metrics_agent(
    payload: AgentRunRequest,
    controller: AgentsController = Depends(get_controller),
) -> dict:
    """Executes the Metrics Agent independently and returns findings."""
    return await controller.run_agent("metrics", payload)


@router.post("/deployment", response_model=dict)
async def run_deployment_agent(
    payload: AgentRunRequest,
    controller: AgentsController = Depends(get_controller),
) -> dict:
    """Executes the Deployment Agent independently and returns findings."""
    return await controller.run_agent("deployment", payload)


@router.post("/review", response_model=dict)
async def run_review_agent(
    payload: AgentRunRequest,
    controller: AgentsController = Depends(get_controller),
) -> dict:
    """Executes the Review Agent independently and returns findings."""
    return await controller.run_agent("review", payload)


@router.post("/root-cause", response_model=dict)
async def run_root_cause_agent(
    payload: AgentRunRequest,
    controller: AgentsController = Depends(get_controller),
) -> dict:
    """Executes the Root Cause Agent independently and returns findings."""
    return await controller.run_agent("root-cause", payload)


@router.post("/recommendation", response_model=dict)
async def run_recommendation_agent(
    payload: AgentRunRequest,
    controller: AgentsController = Depends(get_controller),
) -> dict:
    """Executes the Recommendation Agent independently and returns findings."""
    return await controller.run_agent("recommendation", payload)
