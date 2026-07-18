from langgraph.graph import StateGraph, START, END

from sentinel_api.ai.workflows.state import WorkflowState
from sentinel_api.ai.workflows.nodes import (
    coordinator_node,
    log_node,
    metrics_node,
    deployment_node,
    merge_results_node,
    root_cause_node,
    similar_incidents_node,
    recommendation_node,
    review_node,
)
from sentinel_api.ai.workflows.edges import (
    route_coordinator,
    route_log,
    route_metrics,
    route_deployment,
    route_merge_results,
    route_root_cause,
    route_similar_incidents,
    route_recommendation,
    route_report,
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
    builder.add_node("merge_results", merge_results_node)
    builder.add_node("root_cause", root_cause_node)
    builder.add_node("similar_incidents", similar_incidents_node)
    builder.add_node("recommendation", recommendation_node)
    builder.add_node("report", review_node)

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
            "deployment": "deployment",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "log",
        route_log,
        {
            "log": "log",
            "merge_results": "merge_results",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "metrics",
        route_metrics,
        {
            "metrics": "metrics",
            "merge_results": "merge_results",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "deployment",
        route_deployment,
        {
            "deployment": "deployment",
            "merge_results": "merge_results",
            "__end__": END,
        },
    )

    builder.add_conditional_edges(
        "merge_results",
        route_merge_results,
        {
            "merge_results": "merge_results",
            "root_cause": "root_cause",
            "__end__": END,
        }
    )

    builder.add_conditional_edges(
        "root_cause",
        route_root_cause,
        {
            "root_cause": "root_cause",
            "similar_incidents": "similar_incidents",
            "__end__": END,
        }
    )

    builder.add_conditional_edges(
        "similar_incidents",
        route_similar_incidents,
        {
            "similar_incidents": "similar_incidents",
            "recommendation": "recommendation",
            "__end__": END,
        }
    )

    builder.add_conditional_edges(
        "recommendation",
        route_recommendation,
        {
            "recommendation": "recommendation",
            "report": "report",
            "__end__": END,
        }
    )

    builder.add_conditional_edges(
        "report",
        route_report,
        {
            "report": "report",
            "__end__": END,
        }
    )

    return builder
