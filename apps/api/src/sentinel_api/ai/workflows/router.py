from typing import Union, List
import structlog

from sentinel_api.ai.workflows.state import WorkflowState

logger = structlog.get_logger("sentinel_api.ai.workflows.router")


def check_status_interrupt(state: WorkflowState) -> Union[str, None]:
    status = state.get("status")
    if status in ["CANCELLED", "PAUSED"]:
        logger.info("Routing interrupted due to workflow status", status=status)
        return "__end__"
    return None


def handle_error_routing(state: WorkflowState, node_name: str, next_node: str) -> str:
    """Checks the state for errors of the current node to decide on retry or failure routing.
    If retry is exceeded, it degrades gracefully and moves to the next node.
    """
    status_route = check_status_interrupt(state)
    if status_route:
        return status_route

    timeline = state.get("execution_timeline", [])
    if timeline and timeline[-1].get("node") == node_name and timeline[-1].get("status") == "failed":
        retries = state.get("retry_count", {}).get(node_name, 0)
        max_retries = state.get("intermediate_results", {}).get("max_retries", 2)

        if retries <= max_retries:
            logger.warning(
                "Routing logic: Retrying node",
                node=node_name,
                retry_count=retries,
                max_retries=max_retries,
            )
            return node_name
        else:
            logger.error(
                "Routing logic: Max retries exceeded, degrading gracefully to next node",
                node=node_name,
                next_node=next_node,
                retry_count=retries,
                max_retries=max_retries,
            )
            return next_node
            
    return next_node


def route_coordinator(state: WorkflowState) -> Union[str, List[str]]:
    error_route = handle_error_routing(state, "coordinator", "fan_out")
    if error_route == "fan_out":
        return ["log", "metrics", "deployment"]
    return error_route


def route_log(state: WorkflowState) -> str:
    return handle_error_routing(state, "log", "merge_results")


def route_metrics(state: WorkflowState) -> str:
    return handle_error_routing(state, "metrics", "merge_results")


def route_deployment(state: WorkflowState) -> str:
    return handle_error_routing(state, "deployment", "merge_results")


def route_merge_results(state: WorkflowState) -> str:
    return handle_error_routing(state, "merge_results", "root_cause")


def route_root_cause(state: WorkflowState) -> str:
    return handle_error_routing(state, "root_cause", "similar_incidents")


def route_similar_incidents(state: WorkflowState) -> str:
    return handle_error_routing(state, "similar_incidents", "recommendation")


def route_recommendation(state: WorkflowState) -> str:
    return handle_error_routing(state, "recommendation", "report")


def route_report(state: WorkflowState) -> str:
    return handle_error_routing(state, "report", "__end__")
