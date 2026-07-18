from typing import List, Set
import structlog

from sentinel_api.ai.agents.coordinator.models import AgentStatus, ExecutionPlan

logger = structlog.get_logger("sentinel_api.ai.agents.coordinator.scheduler")


class PlanScheduler:
    """Schedules agent executions in topological layers to support parallel execution."""

    def schedule(self, plan: ExecutionPlan) -> List[List[str]]:
        """Groups agents into batches of parallelizable steps based on their dependencies."""
        logger.info("Scheduling agent execution topology")

        # Select only active agents (exclude pre-skipped ones)
        active_agents = {
            name
            for name, item in plan.items.items()
            if item.status != AgentStatus.SKIPPED
        }

        # Filter dependencies to only include active ones
        dependencies = {}
        for name in active_agents:
            item = plan.items[name]
            dependencies[name] = {
                dep for dep in item.dependencies if dep in active_agents
            }

        batches: List[List[str]] = []
        scheduled: Set[str] = set()

        # Build execution batches (Kahn's/Topological layering)
        while len(scheduled) < len(active_agents):
            current_batch = []
            for name in sorted(active_agents - scheduled):
                if dependencies[name].issubset(scheduled):
                    current_batch.append(name)

            if not current_batch:
                # Cycle or unresolvable dependencies detected
                logger.error(
                    "Cyclic dependency detected in execution plan",
                    scheduled=list(scheduled),
                    remaining=list(active_agents - scheduled),
                )
                raise ValueError("Plan contains cyclic agent dependencies.")

            batches.append(current_batch)
            scheduled.update(current_batch)

            # Assign execution batch index/order to plan items
            batch_order = len(batches) - 1
            for name in current_batch:
                plan.items[name].execution_order = batch_order

        logger.info(
            "Scheduling complete",
            total_batches=len(batches),
            execution_batches=batches,
        )
        return batches
