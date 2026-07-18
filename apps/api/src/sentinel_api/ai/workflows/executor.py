import asyncio
import time
import uuid
from datetime import UTC, datetime
from typing import Any, Dict, Optional
import structlog

from sentinel_api.ai.schemas.models import ExecutionContext, IncidentContext
from sentinel_api.ai.workflows.graph import get_compiled_graph
from sentinel_api.ai.workflows.state import create_initial_state
from sentinel_api.ai.workflows.validators import validate_workflow_state

logger = structlog.get_logger("sentinel_api.ai.workflows.executor")


class WorkflowExecutor:
    """A reusable graph executor for Sentinel AI workflow orchestration.

    Supports:
    - Starting a new workflow run.
    - Pausing execution.
    - Resuming from a checkpoint thread.
    - Cancelling active threads.
    - Retrying specific nodes.
    - Monitoring execution status and duration.
    - Setting timeouts.
    """

    def __init__(self) -> None:
        self.graph = get_compiled_graph()

    async def start(
        self,
        incident: IncidentContext,
        execution_context: ExecutionContext,
        intermediate_results: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Initiates workflow execution, generates a unique execution/thread ID,

        and runs the graph.
        """
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = create_initial_state(incident, execution_context)
        if intermediate_results:
            initial_state["intermediate_results"].update(intermediate_results)

        logger.info(
            "Starting workflow execution",
            thread_id=thread_id,
            incident_id=incident.incident_id,
        )

        return await self._run_graph(initial_state, config, timeout)

    async def resume(
        self,
        thread_id: str,
        state_updates: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Resumes a paused/suspended workflow run using its thread ID."""
        config = {"configurable": {"thread_id": thread_id}}

        # Verify execution checkpoint exists
        current_state = await self.graph.aget_state(config)
        if not current_state.values:
            raise ValueError(f"No execution history found for thread ID: {thread_id}")

        logger.info("Resuming workflow execution", thread_id=thread_id)

        # Apply optional state updates before resuming (e.g. user override)
        if state_updates:
            # When updating state, ensure it goes through the checkpointer
            await self.graph.aupdate_state(config, state_updates)

        # Set status back to RUNNING if it was paused
        state = (await self.graph.aget_state(config)).values
        if state.get("status") == "PAUSED":
            await self.graph.aupdate_state(config, {"status": "RUNNING"})

        # Resuming requires passing inputs=None to continue from checkpoint
        return await self._run_graph(None, config, timeout)

    async def pause(self, thread_id: str) -> Dict[str, Any]:
        """Pauses workflow execution by setting status in checkpointer state to PAUSED."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = await self.graph.aget_state(config)
        if not current_state.values:
            raise ValueError(f"No execution history found for thread ID: {thread_id}")

        state_update = {"status": "PAUSED"}
        await self.graph.aupdate_state(config, state_update)

        logger.info("Workflow paused", thread_id=thread_id)
        updated_state = await self.graph.aget_state(config)
        return {"thread_id": thread_id, "state": updated_state.values}

    async def cancel(self, thread_id: str) -> Dict[str, Any]:
        """Cancels a workflow execution by setting status in checkpointer state to CANCELLED."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = await self.graph.aget_state(config)
        if not current_state.values:
            raise ValueError(f"No execution history found for thread ID: {thread_id}")

        state_update = {"status": "CANCELLED"}
        await self.graph.aupdate_state(config, state_update)

        logger.info("Workflow cancelled", thread_id=thread_id)
        updated_state = await self.graph.aget_state(config)
        return {"thread_id": thread_id, "state": updated_state.values}

    async def retry_node(
        self,
        thread_id: str,
        node_name: str,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Manually triggers a retry of a specific failed node by resetting its retry state

        and resuming the graph.
        """
        config = {"configurable": {"thread_id": thread_id}}
        current_state = await self.graph.aget_state(config)
        if not current_state.values:
            raise ValueError(f"No execution history found for thread ID: {thread_id}")

        state_values = current_state.values

        # Reset retry counter for this node
        retry_counts = dict(state_values.get("retry_count", {}))
        retry_counts[node_name] = 0

        # Remove the latest error if it was for this node
        errors = list(state_values.get("errors", []))
        if errors and errors[-1].get("node") == node_name:
            errors.pop()

        state_update = {
            "retry_count": retry_counts,
            "errors": errors,
            "status": "RUNNING",
            "current_node": node_name,
        }
        await self.graph.aupdate_state(config, state_update)

        logger.info("Retrying node manually", thread_id=thread_id, node=node_name)
        return await self._run_graph(None, config, timeout)

    async def get_status(self, thread_id: str) -> Dict[str, Any]:
        """Fetches the active execution status, current node, and state of a workflow run."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = await self.graph.aget_state(config)
        if not current_state.values:
            return {"thread_id": thread_id, "status": "NOT_FOUND", "state": None}

        state = current_state.values
        return {
            "thread_id": thread_id,
            "status": state.get("status", "UNKNOWN"),
            "current_node": state.get("current_node", ""),
            "visited_nodes": state.get("visited_nodes", []),
            "state": state,
        }

    async def _run_graph(
        self,
        inputs: Optional[Dict[str, Any]],
        config: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Internal runner that invokes the graph, tracks timing/observability,

        manages timeouts, handles exceptions, and validates output state.
        """
        thread_id = config["configurable"]["thread_id"]
        start_time = time.perf_counter()

        try:
            if timeout:
                final_state = await asyncio.wait_for(
                    self.graph.ainvoke(inputs, config), timeout=timeout
                )
            else:
                final_state = await self.graph.ainvoke(inputs, config)

            # Check status; if it completed without getting paused or cancelled,
            # mark status as COMPLETED.
            current_status = final_state.get("status", "RUNNING")
            if current_status not in ["PAUSED", "CANCELLED"]:
                final_state["status"] = "COMPLETED"
                # Save the final COMPLETED state status in the checkpointer
                await self.graph.aupdate_state(config, {"status": "COMPLETED"})

            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "Workflow execution finished",
                thread_id=thread_id,
                status=final_state["status"],
                duration_ms=duration_ms,
            )

            # Validate the final workflow state integrity
            validate_workflow_state(final_state)

            return {
                "thread_id": thread_id,
                "status": final_state["status"],
                "duration_ms": duration_ms,
                "state": final_state,
            }

        except asyncio.TimeoutError:
            logger.error("Workflow execution timed out", thread_id=thread_id)

            error_event = {
                "node": "system",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": f"Workflow execution timed out after {timeout} seconds.",
            }

            state_update = {"status": "FAILED", "errors": [error_event]}
            await self.graph.aupdate_state(config, state_update)

            last_state = await self.graph.aget_state(config)
            return {
                "thread_id": thread_id,
                "status": "FAILED",
                "duration_ms": timeout * 1000 if timeout else 0,
                "error": "TimeoutError",
                "state": last_state.values if last_state else None,
            }

        except Exception as e:
            logger.exception(
                "Workflow execution encountered an unexpected exception",
                thread_id=thread_id,
                error=str(e),
            )

            error_event = {
                "node": "system",
                "timestamp": datetime.now(UTC).isoformat(),
                "message": f"Unexpected exception: {str(e)}",
            }

            state_update = {"status": "FAILED", "errors": [error_event]}
            await self.graph.aupdate_state(config, state_update)

            last_state = await self.graph.aget_state(config)
            return {
                "thread_id": thread_id,
                "status": "FAILED",
                "duration_ms": (time.perf_counter() - start_time) * 1000,
                "error": str(e),
                "state": last_state.values if last_state else None,
            }
