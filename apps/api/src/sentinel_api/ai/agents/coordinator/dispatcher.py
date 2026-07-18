import asyncio
import time
from typing import Any, Dict, Optional
import structlog

from sentinel_api.ai.agents.coordinator.models import AgentStatus
from sentinel_api.ai.agents.coordinator.state_manager import StateManager
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.schemas.models import AgentResult, ExecutionContext, IncidentContext

logger = structlog.get_logger("sentinel_api.ai.agents.coordinator.dispatcher")


class AgentDispatcher:
    """Dispatches execution of specialized agents using placeholders and policies."""

    def __init__(self, state_manager: StateManager) -> None:
        self.state_manager = state_manager

    async def dispatch(
        self,
        agent_name: str,
        incident: IncidentContext,
        execution_context: ExecutionContext,
        inputs: Dict[str, Any],
    ) -> Optional[AgentResult]:
        """Runs the agent execution, checking timeouts, retries, and failure policies."""
        self.state_manager.update_agent_status(agent_name, AgentStatus.RUNNING)
        plan_item = self.state_manager.plan.items[agent_name]

        # Read policies from inputs (Default is RETRY)
        # Supported policies: "RETRY", "SKIP", "ABORT", "CONTINUE"
        policy = inputs.get("failure_policies", {}).get(agent_name, "RETRY")
        max_retries = inputs.get("max_retries", {}).get(agent_name, 2)

        start_time = time.perf_counter()

        while True:
            try:
                timeout_duration = plan_item.timeout
                # Wrap implementation in asyncio.wait_for for timeout enforcement
                result = await asyncio.wait_for(
                    self._run_placeholder_agent(
                        agent_name, incident, execution_context, inputs
                    ),
                    timeout=timeout_duration,
                )

                duration_ms = (time.perf_counter() - start_time) * 1000
                self.state_manager.update_agent_status(
                    agent_name, AgentStatus.COMPLETED
                )
                self.state_manager.log_event(
                    agent_name,
                    "execution_completed",
                    {"duration_ms": duration_ms, "confidence": result.confidence},
                )
                return result

            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                current_retries = plan_item.retries
                is_timeout = isinstance(e, asyncio.TimeoutError)
                error_msg = "TimeoutError" if is_timeout else str(e)

                self.state_manager.log_event(
                    agent_name,
                    "execution_failed",
                    {
                        "duration_ms": duration_ms,
                        "error": error_msg,
                        "attempt": current_retries + 1,
                        "policy_assigned": policy,
                    },
                )

                # Retry policy handler
                if policy == "RETRY" and current_retries < max_retries:
                    self.state_manager.increment_retries(agent_name)
                    await asyncio.sleep(0.05)  # minor backoff pause
                    continue

                # Fallback policy handlers
                if policy == "SKIP":
                    logger.warning("Failure policy SKIP enforced", agent=agent_name)
                    self.state_manager.update_agent_status(
                        agent_name, AgentStatus.SKIPPED
                    )
                    return None

                elif policy == "CONTINUE":
                    logger.warning(
                        "Failure policy CONTINUE enforced", agent=agent_name
                    )
                    self.state_manager.update_agent_status(
                        agent_name, AgentStatus.FAILED
                    )
                    return AgentResult(
                        success=False,
                        output=error_msg,
                        confidence=0.0,
                        reasoning_summary=f"Non-blocking agent failure: {error_msg}",
                        metadata={"agent_name": agent_name, "error": error_msg},
                        processing_time_ms=duration_ms,
                    )

                else:  # ABORT (or exhausted RETRY attempts)
                    logger.error("Failure policy ABORT enforced", agent=agent_name)
                    self.state_manager.update_agent_status(
                        agent_name, AgentStatus.FAILED
                    )
                    raise AgentException(
                        f"Agent '{agent_name}' failed to execute: {error_msg} (Policy: {policy})"
                    ) from e

    async def _run_placeholder_agent(
        self,
        agent_name: str,
        incident: IncidentContext,
        execution_context: ExecutionContext,
        inputs: Dict[str, Any],
    ) -> AgentResult:
        """Placeholder simulation of agent executions.

        Controlled via inputs to mock delay, timeouts, or failure conditions.
        """
        behavior = inputs.get("mock_behavior", {}).get(agent_name, {})

        # Simulate execution latency
        delay = behavior.get("delay", 0.02)
        await asyncio.sleep(delay)

        # Simulate node timeouts
        if behavior.get("simulate_timeout") is True:
            plan_item = self.state_manager.plan.items[agent_name]
            await asyncio.sleep(plan_item.timeout + 1.0)

        # Simulate failures
        fail_attempts = behavior.get("fail_attempts", 0)
        plan_item = self.state_manager.plan.items[agent_name]
        if plan_item.retries < fail_attempts:
            raise ValueError(f"Simulated execution crash for agent: {agent_name}")

        confidence = behavior.get("confidence", 0.8)
        reasoning = behavior.get(
            "reasoning", f"Mock reasoning summary for {agent_name}."
        )

        from sentinel_api.app.reporting.utils import get_current_utc_timestamp
        now = get_current_utc_timestamp()

        # Build realistic structured dictionary outputs
        if agent_name == "Log Agent":
            output_data = {
                "status": "SUCCESS",
                "findings": [
                    {
                        "timestamp": now,
                        "service": "checkout",
                        "pattern_name": "Database connection pool timeout error",
                        "severity": "Critical",
                        "endpoint": "/charge"
                    }
                ],
                "summary": "Database pool timeouts detected.",
                "metadata": {"log_source": "syslog"},
                "statistics": {"lines_parsed": 100}
            }
        elif agent_name == "Metrics Agent":
            output_data = {
                "status": "SUCCESS",
                "findings": [
                    {
                        "timestamp": now,
                        "service": "checkout",
                        "metric_name": "db_connection_failures_count",
                        "severity": "Critical"
                    }
                ],
                "anomaly_clusters": [
                    {
                        "timestamp": now,
                        "service": "checkout",
                        "metric_name": "db_connection_failures_count",
                        "severity": "Critical"
                    }
                ]
            }
        elif agent_name == "Deployment Agent":
            output_data = {
                "status": "SUCCESS",
                "findings": [
                    {
                        "timestamp": now,
                        "service": "checkout",
                        "version": "v1.3.4",
                        "description": "Deployed DB change for checkout (Version: v1.3.4)",
                        "correlation_score": 0.90,
                        "change_type": "DB"
                    }
                ],
                "correlated_events": [
                    {
                        "timestamp": now,
                        "service": "checkout",
                        "version": "v1.3.4",
                        "description": "Deployed DB change for checkout (Version: v1.3.4)",
                        "correlation_score": 0.90,
                        "change_type": "DB"
                    }
                ]
            }
        elif agent_name == "Review Agent":
            output_data = {
                "status": "SUCCESS",
                "findings": [
                    {
                        "category": "Payments",
                        "severity": "Critical",
                        "summary": "Found 5 reports regarding Payments checkout slowness/errors",
                        "affected_features": ["checkout page"]
                    }
                ],
                "metadata": {
                    "timeline_stats": {
                        "first_report": now
                    }
                }
            }
        elif agent_name == "Root Cause Agent":
            output_data = {
                "status": "SUCCESS",
                "root_cause": "BAD_DEPLOYMENT",
                "reasoning_summary": "Bad deployment v1.3.4 caused database pool timeouts",
                "supporting_evidence": ["Deployment v1.3.4 matches time window", "Log timeouts verified"],
                "alternative_hypotheses": [
                    {"root_cause_type": "DATABASE_OVERLOAD", "confidence": 0.65, "description": "High traffic pool overflow"}
                ],
                "confidence": 0.92,
                "metadata": {
                    "incident_timestamp": now
                }
            }
        elif agent_name == "Recommendation Agent":
            output_data = {
                "status": "SUCCESS",
                "incident_priority": "Critical",
                "recommended_actions": [
                    {
                        "id": "act-rollback",
                        "action_type": "ROLLBACK",
                        "title": "Rollback payment-service Deployment",
                        "description": "Initiate rollback of payment-service to last known stable.",
                        "priority": "Critical",
                        "urgency": "Critical",
                        "execution_order": 1,
                        "estimated_impact": "Will eliminate regression",
                        "risk_level": "Medium",
                        "side_effects": ["Transient gateway lag"]
                    }
                ],
                "risk_assessment": {
                    "risk_score": 0.45,
                    "potential_side_effects": ["Transient gateway lag"],
                    "rollback_difficulty": "Medium",
                    "business_impact": "Low",
                    "confidence": 0.88
                },
                "validation_checklist": [
                    {
                        "title": "Verify current version",
                        "command_suggestion": "kubectl get deployments",
                        "success_criteria": "Matches v1.3.4"
                    }
                ],
                "recovery_monitoring_plan": {
                    "metrics_to_watch": ["http_requests_total"],
                    "duration_minutes": 15,
                    "success_criteria": "Error rate < 0.1%"
                },
                "metadata": {
                    "affected_services": ["payment-service"]
                }
            }
        else:
            output_data = {"findings": f"Mock findings from {agent_name}"}

        # Keep short summaries aligned
        output_data["reasoning_summary"] = reasoning

        return AgentResult(
            success=True,
            output=output_data,
            confidence=confidence,
            reasoning_summary=reasoning,
            metadata={"agent_name": agent_name},
            processing_time_ms=delay * 1000,
        )
