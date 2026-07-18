import time
import asyncio
from datetime import UTC, datetime
from typing import Any
import structlog

from sentinel_api.ai.schemas.models import AgentRequest, AgentResult
from sentinel_api.ai.workflows.state import WorkflowState
from sentinel_api.ai.config import ModelConfig

# Import actual agents
from sentinel_api.ai.agents.log_agent.log_agent import LogAgent
from sentinel_api.ai.agents.metrics_agent.metrics_agent import MetricsAgent
from sentinel_api.ai.agents.deployment_agent.deployment_agent import DeploymentAgent
from sentinel_api.ai.agents.root_cause_agent.root_cause_agent import RootCauseAgent
from sentinel_api.ai.agents.recommendation_agent.recommendation_agent import RecommendationAgent
from sentinel_api.ai.agents.review_agent.review_agent import ReviewAgent

logger = structlog.get_logger("sentinel_api.ai.workflows.nodes")

# Singleton agent instances
log_agent_instance = LogAgent()
metrics_agent_instance = MetricsAgent()
deployment_agent_instance = DeploymentAgent()
root_cause_agent_instance = RootCauseAgent()
remediation_agent_instance = RecommendationAgent()
report_agent_instance = ReviewAgent()


def _build_agent_request(state: WorkflowState) -> AgentRequest:
    return AgentRequest(
        execution_context=state["execution_context"],
        incident_context=state["incident"],
        inputs={
            "logs": state.get("logs", []),
            "metrics": state.get("metrics", []),
            "deployment_events": state.get("deployment_events", []),
            "log_analysis": state.get("log_analysis", {}),
            "metrics_analysis": state.get("metrics_analysis", {}),
            "deployment_analysis": state.get("deployment_analysis", {}),
            "root_cause": state.get("root_cause", {}),
            "similar_incidents": state.get("similar_incidents", []),
        }
    )


def create_agent_node(name: str, agent_instance, state_output_key: str):
    """Factory to create a LangGraph node that wraps a BaseAgent."""
    
    async def node_func(state: WorkflowState) -> dict[str, Any]:
        start_time = time.perf_counter()
        timestamp_start = datetime.now(UTC).isoformat()
        logger.info("Entering agent node", node=name, status="started")

        request = _build_agent_request(state)
        config = ModelConfig(provider="openai", model_name="gpt-4")

        # Check for simulated failures/retries (testing support)
        fail_target = state.get("intermediate_results", {}).get("fail_node")
        if fail_target == name:
            current_retries = state.get("retry_count", {}).get(name, 0)
            max_retries = state.get("intermediate_results", {}).get("fail_node_max_retries", 1)
            if current_retries < max_retries:
                logger.warning("Simulating node failure", node=name, retry_count=current_retries)
                new_retry_counts = dict(state.get("retry_count", {}))
                new_retry_counts[name] = current_retries + 1
                
                error_event = {
                    "node": name,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "message": f"Simulated node failure for {name}",
                }
                
                duration_ms = (time.perf_counter() - start_time) * 1000
                return {
                    "current_node": name,
                    "visited_nodes": [name],
                    "retry_count": new_retry_counts,
                    "errors": [error_event],
                    "execution_timeline": [{
                        "node": name,
                        "enter_time": timestamp_start,
                        "exit_time": datetime.now(UTC).isoformat(),
                        "duration_ms": duration_ms,
                        "status": "failed",
                        "error": error_event["message"],
                    }],
                    "agent_status": {name: "failed"}
                }

        try:
            # Execute actual agent
            result_dict = await agent_instance._run(request, config)
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            timestamp_end = datetime.now(UTC).isoformat()

            # Ensure we have a valid AgentResult structure
            agent_result = AgentResult(
                success=True,
                output=result_dict.get("summary", result_dict),
                confidence=result_dict.get("confidence", 0.9),
                reasoning_summary=result_dict.get("reasoning_summary", f"Successfully executed {name}"),
                metadata={"node": name, "timestamp": timestamp_end, **result_dict.get("metadata", {})},
                processing_time_ms=duration_ms,
            )

            state_updates = {
                "current_node": name,
                "visited_nodes": [name],
                "agent_outputs": {name: agent_result},
                "confidence_scores": {name: agent_result.confidence},
                "execution_timeline": [{
                    "node": name,
                    "enter_time": timestamp_start,
                    "exit_time": timestamp_end,
                    "duration_ms": duration_ms,
                    "status": "success",
                    "output_summary": agent_result.reasoning_summary,
                }],
                "agent_status": {name: "success"},
                state_output_key: result_dict
            }
            
            # Special assignments based on node type
            if state_output_key == "generated_report":
                state_updates["generated_report"] = result_dict
            
            logger.info("Exiting workflow node", node=name, status="completed", duration_ms=duration_ms)
            return state_updates

        except Exception as e:
            logger.exception(f"Error in {name}", error=str(e))
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            new_retry_counts = dict(state.get("retry_count", {}))
            new_retry_counts[name] = new_retry_counts.get(name, 0) + 1
            
            error_event = {
                "node": name,
                "timestamp": datetime.now(UTC).isoformat(),
                "message": str(e),
            }
            
            return {
                "current_node": name,
                "visited_nodes": [name],
                "retry_count": new_retry_counts,
                "errors": [error_event],
                "execution_timeline": [{
                    "node": name,
                    "enter_time": timestamp_start,
                    "exit_time": datetime.now(UTC).isoformat(),
                    "duration_ms": duration_ms,
                    "status": "failed",
                    "error": str(e),
                }],
                "agent_status": {name: "failed"}
            }

    return node_func


# Placeholder nodes
async def orchestrator_node(state: WorkflowState) -> dict[str, Any]:
    """Node that initializes the workflow and sets the stage for analysis agents."""
    timestamp = datetime.now(UTC).isoformat()
    return {
        "current_node": "coordinator",
        "visited_nodes": ["coordinator"],
        "agent_status": {"coordinator": "success"},
        "execution_timeline": [{
            "node": "coordinator",
            "enter_time": timestamp,
            "exit_time": timestamp,
            "duration_ms": 10,
            "status": "success",
            "output_summary": "Incident received. Planning execution.",
        }]
    }

async def similar_incidents_node(state: WorkflowState) -> dict[str, Any]:
    """Retrieves similar past incidents from the AI Memory Engine."""
    from sentinel_api.database.session import AsyncSessionLocal
    from sentinel_api.services.memory import MemoryService
    
    timestamp = datetime.now(UTC).isoformat()
    start_time = time.perf_counter()
    
    import uuid
    similar_incidents = []
    
    # We retrieve the memory using the incident summary and workspace context
    incident = state.get("incident")
    workspace_id_raw = getattr(incident, "workspace_id", None)
    if not workspace_id_raw and incident and getattr(incident, "signals", None) and isinstance(incident.signals, dict):
        workspace_id_raw = incident.signals.get("workspace_id")
        
    if incident and workspace_id_raw:
        try:
            workspace_uuid = uuid.UUID(str(workspace_id_raw))
        except ValueError:
            workspace_uuid = None
            
        if workspace_uuid:
            async with AsyncSessionLocal() as session:
                memory_service = MemoryService(session)
                memories = await memory_service.find_similar(
                    workspace_id=workspace_uuid,
                    query_text=incident.summary,
                    limit=3
                )
            # Format the output for the Root Cause Agent
            similar_incidents = [
                {
                    "incident_id": m.incident_id,
                    "summary": m.summary,
                    "root_cause": m.root_cause,
                    "recommended_fix": m.recommended_fix,
                    "tags": [{"name": t.name, "value": t.value} for t in m.tags]
                }
                for m in memories
            ]
            
    duration_ms = (time.perf_counter() - start_time) * 1000

    return {
        "current_node": "similar_incidents",
        "visited_nodes": ["similar_incidents"],
        "similar_incidents": similar_incidents,
        "agent_status": {"similar_incidents": "success"},
        "execution_timeline": [{
            "node": "similar_incidents",
            "enter_time": timestamp,
            "exit_time": datetime.now(UTC).isoformat(),
            "duration_ms": duration_ms,
            "status": "success",
            "output_summary": f"Retrieved {len(similar_incidents)} similar historical incidents.",
        }]
    }

async def merge_results_node(state: WorkflowState) -> dict[str, Any]:
    """Synchronizes parallel executions."""
    timestamp = datetime.now(UTC).isoformat()
    return {
        "current_node": "merge_results",
        "visited_nodes": ["merge_results"],
        "agent_status": {"merge_results": "success"},
        "execution_timeline": [{
            "node": "merge_results",
            "enter_time": timestamp,
            "exit_time": timestamp,
            "duration_ms": 5,
            "status": "success",
            "output_summary": "Successfully merged log, metrics, and deployment analysis.",
        }]
    }


# Instantiate all nodes
coordinator_node = orchestrator_node
log_node = create_agent_node("log", log_agent_instance, "log_analysis")
metrics_node = create_agent_node("metrics", metrics_agent_instance, "metrics_analysis")
deployment_node = create_agent_node("deployment", deployment_agent_instance, "deployment_analysis")
root_cause_node = create_agent_node("root_cause", root_cause_agent_instance, "root_cause")
recommendation_node = create_agent_node("recommendation", remediation_agent_instance, "recommended_actions")
report_node = create_agent_node("report", report_agent_instance, "generated_report")
review_node = report_node
