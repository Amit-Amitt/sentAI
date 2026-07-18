from langgraph.graph import StateGraph, START, END

from sentinel_api.ai.workflows.state import WorkflowState
from sentinel_api.ai.workflows.nodes import (
    coordinator_node,
    log_node,
    metrics_node,
    deployment_node,
    review_node,
    root_cause_node,
    recommendation_node,
)
from sentinel_api.ai.workflows.edges import (
    route_coordinator,
    route_log,
    route_metrics,
    route_deployment,
    route_review,
    route_root_cause,
    route_recommendation,
)


def create_workflow_graph() -> StateGraph:
    """Builds the complete workflow StateGraph, registering all nodes and routing edges.

    Ensures support for sequential execution, conditional branching, retry/failure paths,
    and parallel flow paths.
    """
    builder = StateGraph(WorkflowState)

    # 1. Add all nodes
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("log", log_node)
    builder.add_node("metrics", metrics_node)
    builder.add_node("deployment", deployment_node)
    builder.add_node("review", review_node)
    builder.add_node("root_cause", root_cause_node)
    builder.add_node("recommendation", recommendation_node)

    # 2. Add entry point
    builder.add_edge(START, "coordinator")

    # 3. Add conditional/routing edges
    builder.add_conditional_edges(
        "coordinator",
        route_coordinator,
        {
            "coordinator": "coordinator",  # self-loop for retry
            "log": "log",
            "metrics": "metrics",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "log",
        route_log,
        {
            "log": "log",  # self-loop for retry
            "metrics": "metrics",
            "deployment": "deployment",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "metrics",
        route_metrics,
        {
            "metrics": "metrics",  # self-loop for retry
            "deployment": "deployment",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "deployment",
        route_deployment,
        {
            "deployment": "deployment",  # self-loop for retry
            "review": "review",
            "root_cause": "root_cause",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "review",
        route_review,
        {
            "review": "review",  # self-loop for retry
            "root_cause": "root_cause",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "root_cause",
        route_root_cause,
        {
            "root_cause": "root_cause",  # self-loop for retry
            "recommendation": "recommendation",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "recommendation",
        route_recommendation,
        {
            "recommendation": "recommendation",  # self-loop for retry
            "__end__": END,
        },
    )

    return builder
