import pytest
import uuid
from typing import Dict, Any

from sentinel_api.services.simulation import SimulationLibrary, SimulationService

@pytest.mark.asyncio
async def test_simulation_library_scenarios():
    scenarios = SimulationLibrary.SCENARIOS
    assert len(scenarios) == 10
    
    # Check that all have required keys
    for s in scenarios:
        assert "id" in s
        assert "title" in s
        assert "description" in s
        assert "affected_services" in s
        assert "expected_root_cause" in s

@pytest.mark.asyncio
async def test_generate_synthetic_signals():
    scenario = SimulationLibrary.get_scenario("db_pool_exhausted")
    assert scenario is not None
    
    signals = SimulationLibrary.generate_synthetic_signals(scenario)
    assert "log_agent_output" in signals
    assert "metrics_agent_output" in signals
    
    # Verify specific log was added
    logs = signals["log_agent_output"]
    assert any("remaining connection slots" in log for log in logs)
    
    # Verify specific metric was added
    metrics = signals["metrics_agent_output"]
    assert any("db_connections_active == 1000" in metric for metric in metrics)
