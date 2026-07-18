import asyncio
import time
from typing import Any

from sentinel_api.ai.agents.coordinator.aggregator import ResultAggregator
from sentinel_api.ai.agents.coordinator.dispatcher import AgentDispatcher
from sentinel_api.ai.agents.coordinator.models import AgentStatus
from sentinel_api.ai.agents.coordinator.planner import IncidentPlanner
from sentinel_api.ai.agents.coordinator.scheduler import PlanScheduler
from sentinel_api.ai.agents.coordinator.state_manager import StateManager
from sentinel_api.ai.agents.coordinator.validator import IncidentValidator
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.runtime.agent import BaseAgent
from sentinel_api.ai.schemas.models import AgentRequest


class CoordinatorAgent(BaseAgent):
    """The central orchestrator managing the incident investigation lifecycle

    by planning and coordinating specialized agent runs.
    """

    def __init__(self) -> None:
        super().__init__("Coordinator")
        self.validator = IncidentValidator()
        self.planner = IncidentPlanner()
        self.scheduler = PlanScheduler()
        self.aggregator = ResultAggregator()

    def validate(self, request: AgentRequest) -> None:
        """Validates execution context parameters and the incident context structure."""
        super().validate(request)
        self.validator.validate(request.incident_context)

    async def _run(self, request: AgentRequest, config: ModelConfig) -> Any:
        """Orchestrates validation, planning, scheduling, execution, and aggregation."""
        incident = request.incident_context
        execution_context = request.execution_context
        inputs = request.inputs

        # 1. Plan creation
        plan = self.planner.create_plan(incident)
        state_manager = StateManager(plan)
        dispatcher = AgentDispatcher(state_manager)

        # 2. Scheduling concurrent batches
        batches = self.scheduler.schedule(plan)

        # 3. Concurrent Dispatching
        start_time = time.perf_counter()
        agent_results = {}

        for batch in batches:
            # Support parallel execution by gathering batch dispatches
            tasks = [
                dispatcher.dispatch(
                    agent_name, incident, execution_context, inputs
                )
                for agent_name in batch
            ]
            batch_results = await asyncio.gather(*tasks)

            for agent_name, result in zip(batch, batch_results):
                if result is not None:
                    agent_results[agent_name] = result
                else:
                    state_manager.update_agent_status(
                        agent_name, AgentStatus.SKIPPED
                    )

        total_duration_ms = (time.perf_counter() - start_time) * 1000

        # 4. Aggregating results
        final_state = self.aggregator.aggregate(
            incident, agent_results, state_manager, total_duration_ms
        )

        # Return dict representation of FinalExecutionState
        return final_state.model_dump()
