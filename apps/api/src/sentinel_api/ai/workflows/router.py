from typing import Union, List
import structlog

from sentinel_api.ai.workflows.state import WorkflowState

logger = structlog.get_logger("sentinel_api.ai.workflows.router")


def check_status_interrupt(state: WorkflowState) -> Union[str, None]:
    """Checks if the workflow status requires aborting or pausing the execution path.

    Returns:
        '__end__' if status is CANCELLED or PAUSED, otherwise None.
    """
    status = state.get("status")
    if status in ["CANCELLED", "PAUSED"]:
        logger.info("Routing interrupted due to workflow status", status=status)
        return "__end__"
    return None


def handle_error_routing(state: WorkflowState, node_name: str) -> Union[str, None]:
    """Checks the state for errors of the current node to decide on retry or failure routing.

    Returns:
        The node name to retry, '__end__' if retries exceeded, or None if no error.
    """
    # First check status interrupt
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
                "Routing logic: Max retries exceeded, routing to failure state/END",
                node=node_name,
                retry_count=retries,
                max_retries=max_retries,
            )
            return "__end__"
    return None


def route_coordinator(state: WorkflowState) -> Union[str, List[str]]:
    """Determines routing after the Coordinator node.

    Supports:
    - Parallel execution: returns ['log', 'metrics'] if state indicates parallel execution.
    - Conditional execution: skips metrics if 'skip_metrics' is in intermediate results.
    - Sequential default: routes to 'log'.
    """
    error_route = handle_error_routing(state, "coordinator")
    if error_route:
        return error_route

    # Check for parallel execution override
    if state.get("intermediate_results", {}).get("parallel", False):
        logger.info("Routing coordinator to parallel branches: log and metrics")
        return ["log", "metrics"]

    # Check for conditional branch
    if state.get("intermediate_results", {}).get("branch") == "skip_metrics":
        logger.info("Routing coordinator: skip_metrics conditional branch taken")
        return "log"  # coordinator -> log -> deployment (skipping metrics branch)

    logger.info("Routing coordinator: default sequential path to log")
    return "log"


def route_log(state: WorkflowState) -> str:
    """Determines routing after the Log node."""
    error_route = handle_error_routing(state, "log")
    if error_route:
        return error_route

    # If parallel mode is active or skip_metrics is requested, route to deployment.
    # Otherwise, standard sequential execution routes: coordinator -> log -> metrics.
    is_parallel = state.get("intermediate_results", {}).get("parallel", False)
    is_skip_metrics = (
        state.get("intermediate_results", {}).get("branch") == "skip_metrics"
    )

    if is_parallel or is_skip_metrics:
        logger.info(
            "Routing log: routing to deployment",
            parallel=is_parallel,
            skip_metrics=is_skip_metrics,
        )
        return "deployment"

    logger.info("Routing log (sequential mode): routing to metrics")
    return "metrics"


def route_metrics(state: WorkflowState) -> str:
    """Determines routing after the Metrics node."""
    error_route = handle_error_routing(state, "metrics")
    if error_route:
        return error_route

    logger.info("Routing metrics: routing to deployment")
    return "deployment"


def route_deployment(state: WorkflowState) -> str:
    """Determines routing after the Deployment node.

    Supports:
    - Conditional branching: skips review if 'skip_review' is in intermediate results.
    - Sequential default: routes to 'review'.
    """
    error_route = handle_error_routing(state, "deployment")
    if error_route:
        return error_route

    if state.get("intermediate_results", {}).get("branch") == "skip_review":
        logger.info("Routing deployment: skip_review conditional branch taken")
        return "root_cause"

    logger.info("Routing deployment: default sequential path to review")
    return "review"


def route_review(state: WorkflowState) -> str:
    """Determines routing after the Review node."""
    error_route = handle_error_routing(state, "review")
    if error_route:
        return error_route

    logger.info("Routing review: routing to root_cause")
    return "root_cause"


def route_root_cause(state: WorkflowState) -> str:
    """Determines routing after the RootCause node."""
    error_route = handle_error_routing(state, "root_cause")
    if error_route:
        return error_route

    logger.info("Routing root_cause: routing to recommendation")
    return "recommendation"


def route_recommendation(state: WorkflowState) -> str:
    """Determines routing after the Recommendation node."""
    error_route = handle_error_routing(state, "recommendation")
    if error_route:
        return error_route

    logger.info("Routing recommendation: routing to END")
    return "__end__"
