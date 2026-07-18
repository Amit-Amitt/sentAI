import pytest
from datetime import datetime, UTC, timedelta
from sentinel_api.ai.agents.deployment_agent import DeploymentAgent
from sentinel_api.ai.agents.deployment_agent.schemas import DeploymentEvent
from sentinel_api.ai.agents.deployment_agent.deployment_parser import DeploymentParser
from sentinel_api.ai.agents.deployment_agent.timeline_builder import TimelineBuilder
from sentinel_api.ai.agents.deployment_agent.change_detector import ChangeDetector
from sentinel_api.ai.agents.deployment_agent.config_change_detector import ConfigChangeDetector
from sentinel_api.ai.agents.deployment_agent.feature_flag_analyzer import FeatureFlagAnalyzer
from sentinel_api.ai.agents.deployment_agent.rollback_detector import RollbackDetector
from sentinel_api.ai.agents.deployment_agent.release_analyzer import ReleaseAnalyzer
from sentinel_api.ai.agents.deployment_agent.correlation_engine import CorrelationEngine
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)


@pytest.fixture
def sample_deployments():
    now = datetime.now(UTC)
    return [
        {
            "id": "dep-1",
            "service": "user-service",
            "version": "v1.2.3",
            "environment": "prod",
            "timestamp": (now - timedelta(minutes=45)).isoformat(),
            "change_type": "APP",
            "status": "SUCCESS",
            "commits": ["fix: user login", "breaking: change auth token format"],
            "files_changed": 12,
        },
        {
            "id": "dep-2",
            "service": "payment-gateway",
            "version": "v2.0.0",
            "environment": "prod",
            "timestamp": (now - timedelta(minutes=8)).isoformat(),
            "change_type": "DB",
            "status": "SUCCESS",
            "strategy": "canary",
            "migration": True,
        },
        {
            "id": "dep-3",
            "service": "notification-worker",
            "version": "v0.9.1",
            "environment": "prod",
            "timestamp": (now - timedelta(minutes=5)).isoformat(),
            "change_type": "CONFIG",
            "status": "ROLLBACK",
            "keys_changed": ["database_secret_key"],
            "is_secret": True,
        },
        {
            "id": "dep-4",
            "service": "api-gateway",
            "version": "v1.5.0",
            "environment": "prod",
            "timestamp": (now - timedelta(minutes=2)).isoformat(),
            "change_type": "FLAG",
            "status": "SUCCESS",
            "flag_name": "enable-new-routing",
            "old_percentage": 0,
            "new_percentage": 100,
        },
    ]


def test_deployment_parser(sample_deployments):
    parser = DeploymentParser()
    events = parser.parse(sample_deployments)

    assert len(events) == 4
    assert events[0].deployment_id == "dep-1"
    assert events[0].service == "user-service"
    assert events[0].change_type == "APP"
    assert events[1].change_type == "DB"
    assert events[2].change_type == "CONFIG"
    assert events[2].status == "ROLLBACK"
    assert events[3].change_type == "FLAG"


def test_timeline_builder(sample_deployments):
    parser = DeploymentParser()
    builder = TimelineBuilder()

    events = parser.parse(sample_deployments)
    incident_time = datetime.now(UTC).isoformat()

    timeline = builder.build_timeline(events, incident_time)
    assert len(timeline) == 4
    # Chronological sort: dep-1 (45m ago) -> dep-2 (8m ago) -> dep-3 (5m ago) -> dep-4 (2m ago)
    assert timeline[0].service == "user-service"
    assert "CRITICAL TIMING" in timeline[3].description  # 2m before incident
    assert "HIGH TIMING PROXIMITY" in timeline[0].description  # 45m before incident


def test_change_detector(sample_deployments):
    parser = DeploymentParser()
    detector = ChangeDetector()

    events = parser.parse(sample_deployments)
    classified = detector.detect_changes(events)

    assert len(classified["APP"]) == 1
    assert len(classified["DB"]) == 1
    assert len(classified["CONFIG"]) == 1
    assert len(classified["FLAG"]) == 1


def test_config_change_detector(sample_deployments):
    parser = DeploymentParser()
    detector = ConfigChangeDetector()

    events = parser.parse(sample_deployments)
    classified = ChangeDetector().detect_changes(events)
    config_findings = detector.analyze_config_changes(classified["CONFIG"])

    assert len(config_findings) == 1
    assert config_findings[0]["is_secret"] is True
    assert config_findings[0]["risk_level"] == "High"


def test_feature_flag_analyzer(sample_deployments):
    parser = DeploymentParser()
    analyzer = FeatureFlagAnalyzer()

    events = parser.parse(sample_deployments)
    classified = ChangeDetector().detect_changes(events)
    flag_findings = analyzer.analyze_flags(classified["FLAG"])

    assert len(flag_findings) == 1
    assert flag_findings[0]["flag_name"] == "enable-new-routing"
    assert flag_findings[0]["risk_level"] == "High"  # Ramped up from 0 to 100%


def test_rollback_detector(sample_deployments):
    parser = DeploymentParser()
    detector = RollbackDetector()

    events = parser.parse(sample_deployments)
    rollback_findings = detector.detect_rollbacks(events)

    assert len(rollback_findings) == 1
    assert rollback_findings[0]["issue_type"] == "ROLLBACK"
    assert rollback_findings[0]["service"] == "notification-worker"


def test_release_analyzer(sample_deployments):
    parser = DeploymentParser()
    analyzer = ReleaseAnalyzer()

    events = parser.parse(sample_deployments)
    risks = analyzer.analyze_releases(events)

    assert risks["dep-1"]["has_breaking"] is True
    assert risks["dep-1"]["risk_score"] == 0.7  # breaking + large size
    assert risks["dep-2"]["has_migration"] is True


def test_correlation_engine(sample_deployments):
    parser = DeploymentParser()
    analyzer = ReleaseAnalyzer()
    engine = CorrelationEngine()

    events = parser.parse(sample_deployments)
    risks = analyzer.analyze_releases(events)
    incident_time = datetime.now(UTC).isoformat()

    findings = engine.correlate(events, incident_time, risks)

    # All should be correlated because they happened recently before incident
    assert len(findings) == 4
    # Highest correlation should be the one closest in time with high risk (dep-4 or dep-2)
    assert findings[0].correlation_score > 0.5


@pytest.mark.asyncio
async def test_deployment_agent_end_to_end(sample_deployments):
    agent = DeploymentAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-dep-1",
        correlation_id="corr-dep-2",
        agent_id="test-dep-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-dep-3",
        severity="SEV1",
        status="active",
        summary="API Gateway routing error",
        signals={"raw_deployments": sample_deployments, "incident_time": datetime.now(UTC).isoformat()}
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)

    assert result.success is True
    assert result.output["agent_name"] == "Deployment Agent"
    assert len(result.output["findings"]) == 4
    assert len(result.output["deployment_timeline"]) == 4
    assert result.output["summary"]["short_summary"].startswith("Deployment analysis completed")
    assert any("Secret updated on service" in r for r in result.output["summary"]["detected_risks"])


@pytest.mark.asyncio
async def test_deployment_agent_validation_failures():
    agent = DeploymentAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-dep-1",
        correlation_id="corr-dep-2",
        agent_id="test-dep-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-dep-3",
        severity="SEV1",
        status="active",
        summary="API Gateway routing error"
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)
    assert result.success is False
    assert "Deployment data is missing" in result.reasoning_summary
