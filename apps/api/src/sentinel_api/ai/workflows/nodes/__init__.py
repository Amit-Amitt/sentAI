import time
from datetime import UTC, datetime
from typing import Any
import structlog

from sentinel_api.ai.schemas.models import AgentResult
from sentinel_api.ai.workflows.state import WorkflowState

logger = structlog.get_logger("sentinel_api.ai.workflows.nodes")


def create_placeholder_node(name: str):
    """Factory to create standard placeholder nodes with state tracking, timeline logging,

    and support for simulated failures/retries to enable robust testing.
    """

    async def node_func(state: WorkflowState) -> dict[str, Any]:
        start_time = time.perf_counter()
        timestamp_start = datetime.now(UTC).isoformat()

        logger.info("Entering workflow node", node=name, status="started")

        # Check if we should simulate a failure for this node
        fail_target = state.get("intermediate_results", {}).get("fail_node")
        if fail_target == name:
            # Check retry count
            current_retries = state.get("retry_count", {}).get(name, 0)
            max_retries_to_fail = state.get("intermediate_results", {}).get(
                "fail_node_max_retries", 1
            )
            if current_retries < max_retries_to_fail:
                logger.warning(
                    "Simulating node failure",
                    node=name,
                    retry_count=current_retries,
                )
                # Increment retry count
                new_retry_counts = dict(state.get("retry_count", {}))
                new_retry_counts[name] = current_retries + 1

                # Append error to timeline/errors
                error_event = {
                    "node": name,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "message": f"Simulated node failure for {name}",
                }

                duration_ms = (time.perf_counter() - start_time) * 1000
                timestamp_end = datetime.now(UTC).isoformat()

                return {
                    "current_node": name,
                    "visited_nodes": [name],
                    "retry_count": new_retry_counts,
                    "errors": [error_event],
                    "execution_timeline": [
                        {
                            "node": name,
                            "enter_time": timestamp_start,
                            "exit_time": timestamp_end,
                            "duration_ms": duration_ms,
                            "status": "failed",
                            "error": f"Simulated node failure for {name}",
                        }
                    ],
                }

        # Create mock AgentResult
        duration_ms = (time.perf_counter() - start_time) * 1000
        timestamp_end = datetime.now(UTC).isoformat()

        agent_result = AgentResult(
            success=True,
            output=f"Mock output from {name} node.",
            confidence=0.9,
            reasoning_summary=f"Successfully executed the placeholder logic for node: {name}.",
            metadata={"node": name, "timestamp": timestamp_end},
            processing_time_ms=duration_ms,
        )

        new_outputs = dict(state.get("agent_outputs", {}))
        new_outputs[name] = agent_result

        new_confidences = dict(state.get("confidence_scores", {}))
        new_confidences[name] = 0.9

        logger.info(
            "Exiting workflow node",
            node=name,
            status="completed",
            duration_ms=duration_ms,
        )

        return {
            "current_node": name,
            "visited_nodes": [name],
            "agent_outputs": new_outputs,
            "confidence_scores": new_confidences,
            "execution_timeline": [
                {
                    "node": name,
                    "enter_time": timestamp_start,
                    "exit_time": timestamp_end,
                    "duration_ms": duration_ms,
                    "status": "success",
                }
            ],
        }

    return node_func


# Instantiate the placeholder nodes for the pipeline
coordinator_node = create_placeholder_node("coordinator")
log_node = create_placeholder_node("log")
metrics_node = create_placeholder_node("metrics")
deployment_node = create_placeholder_node("deployment")
review_node = create_placeholder_node("review")
root_cause_node = create_placeholder_node("root_cause")
recommendation_node = create_placeholder_node("recommendation")
