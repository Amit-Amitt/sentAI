import pytest
from sentinel_api.ai.agents.recommendation_agent import RecommendationAgent
from sentinel_api.ai.agents.recommendation_agent.action_generator import ActionGenerator
from sentinel_api.ai.agents.recommendation_agent.priority_engine import PriorityEngine
from sentinel_api.ai.agents.recommendation_agent.risk_assessor import RiskAssessor
from sentinel_api.ai.agents.recommendation_agent.impact_analyzer import ImpactAnalyzer
from sentinel_api.ai.agents.recommendation_agent.rollback_advisor import RollbackAdvisor
from sentinel_api.ai.agents.recommendation_agent.runbook_matcher import RunbookMatcher
from sentinel_api.ai.agents.recommendation_agent.playbook_selector import PlaybookSelector
from sentinel_api.ai.agents.recommendation_agent.validation_checker import ValidationChecker
from sentinel_api.ai.agents.recommendation_agent.summary_generator import SummaryGenerator
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)


@pytest.fixture
def mock_root_cause_output():
    return {
        "root_cause": "Bad Deployment of payment-service",
        "confidence": 0.88,
        "evidence_sources": ["LOG", "METRICS", "DEPLOYMENT", "REVIEW"]
    }


def test_action_generator():
    gen = ActionGenerator()
    actions = gen.generate_actions("Bad Deployment of payment-service", ["payment-service"])

    assert len(actions) >= 2
    types = [a.action_type for a in actions]
    assert "ROLLBACK" in types
    assert "NOTIFY" in types


def test_priority_engine():
    gen = ActionGenerator()
    pe = PriorityEngine()

    actions = gen.generate_actions("Bad Deployment of payment-service", ["payment-service"])
    res = pe.prioritize(actions, "SEV1")

    assert res["incident_priority"] == "Critical"
    assert res["execution_order"][0] == "act-rollback"
    assert len(res["prioritized_actions"]) == len(actions)


def test_risk_assessor():
    gen = ActionGenerator()
    ra = RiskAssessor()

    actions = gen.generate_actions("Bad Deployment of payment-service", ["payment-service"])
    assessment = ra.assess_risk(actions, 0.85)

    assert assessment.confidence == 0.85
    assert assessment.rollback_difficulty == "Medium"
    assert assessment.risk_score < 0.5


def test_impact_analyzer():
    gen = ActionGenerator()
    ia = ImpactAnalyzer()

    actions = gen.generate_actions("Bad Deployment of payment-service", ["payment-service"])
    impact = ia.analyze_impact(["payment-service"], actions, "Critical")

    assert impact["estimated_recovery_time_minutes"] == 15
    assert impact["customer_impact_level"] == "High"


def test_rollback_advisor():
    ra = RollbackAdvisor()
    advice = ra.get_rollback_advice("Bad Deployment of payment-service", ["payment-service"])

    assert "helm rollback" in advice["rollback_command"]
    assert len(advice["verification_steps"]) > 0


def test_runbook_matcher_and_playbook_selector():
    matcher = RunbookMatcher()
    selector = PlaybookSelector()

    runbook = matcher.match_runbook("Database Overload")
    assert runbook["runbook_id"] == "RB-DB-001"

    playbook = selector.select_playbook("DATABASE_OVERLOAD")
    assert playbook["playbook_id"] == "PB-DB-02"


def test_validation_checker():
    vc = ValidationChecker()
    checks = vc.generate_validation_checks("BAD_DEPLOYMENT", ["payment-service"])

    assert len(checks) >= 2
    titles = [c.title for c in checks]
    assert any("Verify current deployment version" in t for t in titles)


def test_summary_generator():
    gen = ActionGenerator()
    sg = SummaryGenerator()

    actions = gen.generate_actions("Bad Deployment of payment-service", ["payment-service"])
    sums = sg.generate_summaries("Bad Deployment of payment-service", "Critical", ["payment-service"], actions)

    assert "Mitigation plan initiated for payment-service" in sums["executive_summary"]
    assert "technical response playbook" in sums["technical_summary"].lower()


@pytest.mark.asyncio
async def test_recommendation_agent_end_to_end(mock_root_cause_output):
    agent = RecommendationAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-rec-1",
        correlation_id="corr-rec-2",
        agent_id="test-rec-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-rec-3",
        severity="SEV1",
        status="active",
        summary="Rollback recommendation deployment",
        signals={"root_cause_agent_output": mock_root_cause_output}
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)

    assert result.success is True
    assert result.output["agent_name"] == "Recommendation Agent"
    assert result.output["incident_priority"] == "Critical"
    assert result.output["execution_order"][0] == "act-rollback"
    assert len(result.output["validation_checklist"]) >= 2
    assert "http_requests_total" in result.output["recovery_monitoring_plan"]["metrics_to_watch"]


@pytest.mark.asyncio
async def test_recommendation_agent_validation_failures():
    agent = RecommendationAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-rec-1",
        correlation_id="corr-rec-2",
        agent_id="test-rec-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-rec-3",
        severity="SEV1",
        status="active",
        summary="No root cause diagnosis"
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)
    assert result.success is False
    assert "requires a diagnosed root cause input" in result.reasoning_summary
