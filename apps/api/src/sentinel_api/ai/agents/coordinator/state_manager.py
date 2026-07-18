from datetime import UTC, datetime
from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.coordinator.models import AgentStatus, ExecutionPlan

logger = structlog.get_logger("sentinel_api.ai.agents.coordinator.state_manager")


class StateManager:
    """Manages the operational lifecycle state of all coordinated agents."""

    def __init__(self, plan: ExecutionPlan) -> None:
        self.plan = plan
        self.timeline: List[Dict[str, Any]] = []

    def update_agent_status(self, agent_name: str, status: AgentStatus) -> None:
        """Updates the status of a scheduled agent and logs it to the timeline."""
        if agent_name not in self.plan.items:
            raise ValueError(f"Agent '{agent_name}' is not in the execution plan.")

        old_status = self.plan.items[agent_name].status
        self.plan.items[agent_name].status = status

        event = {
            "agent_name": agent_name,
            "event": "status_change",
            "from": old_status.value,
            "to": status.value,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.timeline.append(event)
        logger.info(
            "Updated agent execution status",
            agent_name=agent_name,
            from_status=old_status.value,
            to_status=status.value,
        )

    def increment_retries(self, agent_name: str) -> int:
        """Increments and returns the retry counter for the target agent."""
        if agent_name not in self.plan.items:
            raise ValueError(f"Agent '{agent_name}' is not in the execution plan.")

        self.plan.items[agent_name].retries += 1
        new_retries = self.plan.items[agent_name].retries

        event = {
            "agent_name": agent_name,
            "event": "retry",
            "retry_count": new_retries,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self.timeline.append(event)
        logger.warning(
            "Agent retry incremented",
            agent_name=agent_name,
            retry_count=new_retries,
        )
        return new_retries

    def log_event(
        self, agent_name: str, event_type: str, details: Dict[str, Any]
    ) -> None:
        """Appends a custom telemetry event to the execution timeline."""
        event = {
            "agent_name": agent_name,
            "event": event_type,
            "timestamp": datetime.now(UTC).isoformat(),
            **details,
        }
        self.timeline.append(event)
        logger.info(
            "Telemetry event logged",
            agent_name=agent_name,
            event_type=event_type,
            **details,
        )

    def get_pending_agents(self) -> List[str]:
        return [
            name
            for name, item in self.plan.items.items()
            if item.status == AgentStatus.PENDING
        ]

    def get_running_agents(self) -> List[str]:
        return [
            name
            for name, item in self.plan.items.items()
            if item.status == AgentStatus.RUNNING
        ]

    def get_completed_agents(self) -> List[str]:
        return [
            name
            for name, item in self.plan.items.items()
            if item.status == AgentStatus.COMPLETED
        ]

    def get_failed_agents(self) -> List[str]:
        return [
            name
            for name, item in self.plan.items.items()
            if item.status == AgentStatus.FAILED
        ]

    def get_skipped_agents(self) -> List[str]:
        return [
            name
            for name, item in self.plan.items.items()
            if item.status == AgentStatus.SKIPPED
        ]
