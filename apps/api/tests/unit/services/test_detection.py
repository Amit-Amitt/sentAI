import pytest
import uuid
import datetime
from unittest.mock import patch, MagicMock, AsyncMock

from sentinel_api.services.detection import DetectionEngine, TelemetryNormalizer, RuleEngine, SeverityEngine, IncidentCorrelator, AnomalyDetector
from sentinel_api.models.incident import DetectionRule, Incident

@pytest.mark.asyncio
async def test_telemetry_normalizer():
    raw_data = [{"level": "error", "message": "Connection timeout", "timestamp": "2026-07-18T10:00:00Z"}]
    normalized = TelemetryNormalizer.normalize("logs", raw_data)
    
    assert len(normalized) == 1
    assert normalized[0]["type"] == "event"
    assert normalized[0]["level"] == "error"
    assert normalized[0]["message"] == "Connection timeout"

def test_anomaly_detector_zscore():
    values = [10.0, 12.0, 11.0, 10.5, 11.5, 10.0, 12.0]
    # Test normal value
    assert not AnomalyDetector.is_anomalous_zscore(values, 11.0, threshold=3.0)
    # Test anomaly value (mean ~11, std_dev ~0.8)
    assert AnomalyDetector.is_anomalous_zscore(values, 50.0, threshold=3.0)

def test_severity_engine():
    rule = DetectionRule(severity="Medium", target_metric="cpu_usage", operator=">", threshold=80.0)
    
    # Base severity
    assert SeverityEngine.calculate_severity(rule, 85.0) == "Medium"
    
    # Escalated severity > threshold * 2
    assert SeverityEngine.calculate_severity(rule, 165.0) == "High"
    
    # Critical severity > threshold * 5
    assert SeverityEngine.calculate_severity(rule, 405.0) == "Critical"

@pytest.mark.asyncio
@patch("sentinel_api.services.detection.AsyncSessionLocal")
async def test_evaluate_telemetry_creates_incident(mock_db_session):
    # Setup mock rule
    project_id = str(uuid.uuid4())
    workspace_id = str(uuid.uuid4())
    
    # Mock refresh to make it awaitable
    session_instance = mock_db_session.return_value.__aenter__.return_value
    session_instance.refresh = AsyncMock()

    # Since we can't fully run the DB in this mock, we will just patch evaluate_static_rule
    with patch.object(RuleEngine, 'evaluate_static_rule', return_value=15.0):
        with patch.object(IncidentCorrelator, 'get_or_create_incident') as mock_correlate:
            mock_incident = Incident(id=uuid.uuid4(), severity="High")
            mock_correlate.return_value = mock_incident
            
            with patch("sentinel_api.services.detection.IntegrationTriggerService.trigger_workflow") as mock_trigger:
                
                payload_type = "events"
                data = [{"name": "EXCEPTION", "timestamp": "2026-07-18T10:00:00Z"}]
                
                await DetectionEngine.evaluate_telemetry(project_id, workspace_id, payload_type, data)
                
                # Assert that correlation logic was called to prevent duplicates
                assert mock_correlate.called
                
                # Assert that the LangGraph workflow was triggered
                assert mock_trigger.called
