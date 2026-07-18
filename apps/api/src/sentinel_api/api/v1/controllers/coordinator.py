from fastapi import HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from sentinel_api.ai.workflows.executor import WorkflowExecutor
from sentinel_api.ai.schemas.models import (
    ExecutionContext,
    IncidentContext,
)
from sentinel_api.api.v1.validators.schemas import CoordinatorRunRequest


class WorkflowController:
    """Controller handling manual LangGraph Workflow execution invocations."""

    def __init__(self) -> None:
        self.executor = WorkflowExecutor()

    async def run(self, payload: CoordinatorRunRequest) -> dict:
        """Executes the workflow graph and returns the execution thread."""
        try:
            exec_ctx = ExecutionContext(
                request_id=payload.execution_context.get("request_id") or "manual-req",
                correlation_id=payload.execution_context.get("correlation_id") or "manual-corr",
                agent_id="langgraph-orchestrator",
            )
            incident_ctx = IncidentContext(
                incident_id=payload.incident_context.get("incident_id") or "INC-MANUAL",
                severity=payload.incident_context.get("severity") or "SEV2",
                status=payload.incident_context.get("status") or "active",
                summary=payload.incident_context.get("summary") or "Manual test run",
                signals=payload.incident_context.get("signals") or {},
            )
            
            # Start workflow in background or await it
            # The executor.start creates a thread ID
            result = await self.executor.start(
                incident=incident_ctx,
                execution_context=exec_ctx,
                intermediate_results=payload.inputs or {}
            )
            
            # Legacy compatibility fields for tests/clients
            state_data = result.get("state", {})
            result["agent_results"] = state_data.get("agent_outputs", {})
            result["incident_summary"] = state_data.get("incident_title", incident_ctx.summary)
            
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_status(self, thread_id: str) -> dict:
        """Exposes the live execution timeline to the dashboard."""
        try:
            return await self.executor.get_status(thread_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
