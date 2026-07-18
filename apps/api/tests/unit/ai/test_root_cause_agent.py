import pytest
from datetime import datetime, UTC, timedelta
from sentinel_api.ai.agents.root_cause_agent import RootCauseAgent
from sentinel_api.ai.agents.root_cause_agent.evidence_collector import EvidenceCollector
from sentinel_api.ai.agents.root_cause_agent.correlation_engine import CorrelationEngine
from sentinel_api.ai.agents.root_cause_agent.timeline_analyzer import TimelineAnalyzer
from sentinel_api.ai.agents.root_cause_agent.hypothesis_generator import HypothesisGenerator
from sentinel_api.ai.agents.root_cause_agent.hypothesis_ranker import HypothesisRanker
from sentinel_api.ai.agents.root_cause_agent.conflict_resolver import ConflictResolver
from sentinel_api.ai.agents.root_cause_agent.confidence_engine import ConfidenceEngine
from sentinel_api.ai.agents.root_cause_agent.explanation_generator import ExplanationGenerator
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)


@pytest.fixture
def mock_sub_agents_output():
    now = datetime.now(UTC)
    
    # 1. Log Agent mock finding
    log_output = {
        "success": True,
        "confidence": 0.85,
        "findings": [
            {
                "timestamp": (now - timedelta(minutes=8)).isoformat(),
                "service": "payment-service",
                "pattern_name": "Database connection pool timeout error",
                "severity": "Critical",
                "endpoint": "/pay/charge"
            }
        ],
        "metadata": {"incident_timestamp": now.isoformat()}
    }

    # 2. Metrics Agent mock finding
    metrics_output = {
        "success": True,
        "confidence": 0.90,
        "anomaly_clusters": [
            {
                "timestamp": (now - timedelta(minutes=9)).isoformat(),
                "service": "payment-service",
                "metric_name": "db_connection_failures_count",
                "severity": "Critical"
            }
        ],
        "metadata": {"incident_timestamp": now.isoformat()}
    }

    # 3. Deployment Agent mock finding
    deployment_output = {
        "success": True,
        "confidence": 0.95,
        "correlated_events": [
            {
                "timestamp": (now - timedelta(minutes=15)).isoformat(),
                "service": "payment-service",
                "version": "v1.3.4",
                "description": "Deployed DB change for payment-service (Version: v1.3.4)",
                "correlation_score": 0.90,
                "change_type": "DB"
            }
        ],
        "metadata": {"incident_timestamp": now.isoformat()}
    }

    # 4. Review Agent mock finding
    review_output = {
        "success": True,
        "confidence": 0.80,
        "findings": [
            {
                "category": "Payments",
                "severity": "Critical",
                "mentions": 5,
                "affected_services": ["payment-service"],
                "affected_features": ["checkout page"],
                "endpoints": ["/pay/charge"],
                "summary": "Found 5 reports regarding Payments checkout slowness/errors"
            }
        ],
        "metadata": {
            "timeline_stats": {
                "first_report": (now - timedelta(minutes=6)).isoformat()
            }
        }
    }

    return {
        "log_agent_output": log_output,
        "metrics_agent_output": metrics_output,
        "deployment_agent_output": deployment_output,
        "review_agent_output": review_output
    }


def test_evidence_collector(mock_sub_agents_output):
    collector = EvidenceCollector()
    normalized = collector.collect_and_normalize(mock_sub_agents_output)

    assert len(normalized) == 4
    # Chronological sort order: Deployment (15m) -> Metrics (9m) -> Log (8m) -> Review (6m)
    assert normalized[0]["agent"] == "DEPLOYMENT"
    assert normalized[1]["agent"] == "METRICS"
    assert normalized[2]["agent"] == "LOG"
    assert normalized[3]["agent"] == "REVIEW"


def test_correlation_engine(mock_sub_agents_output):
    collector = EvidenceCollector()
    engine = CorrelationEngine()

    normalized = collector.collect_and_normalize(mock_sub_agents_output)
    correlations = engine.find_correlations(normalized)

    # All sub-agents pointed to payment-service
    assert "payment-service" in correlations["services"]
    assert len(correlations["services"]["payment-service"]) == 4
    assert "/pay/charge" in correlations["endpoints"]


def test_timeline_analyzer(mock_sub_agents_output):
    collector = EvidenceCollector()
    analyzer = TimelineAnalyzer()

    normalized = collector.collect_and_normalize(mock_sub_agents_output)
    timeline = analyzer.build_cause_effect_timeline(normalized)

    assert len(timeline) == 4
    # check causality annotation strings
    assert "preceding deployment" in timeline[1]
    assert "support volume" in timeline[3]


def test_hypothesis_generator_and_ranker(mock_sub_agents_output):
    collector = EvidenceCollector()
    engine = CorrelationEngine()
    gen = HypothesisGenerator()
    ranker = HypothesisRanker()

    normalized = collector.collect_and_normalize(mock_sub_agents_output)
    correlations = engine.find_correlations(normalized)

    hypotheses = gen.generate_hypotheses(normalized, correlations)
    assert len(hypotheses) >= 2

    # Verify BAD_DEPLOYMENT and DATABASE_OVERLOAD are generated
    types = [h.root_cause_type for h in hypotheses]
    assert "BAD_DEPLOYMENT" in types
    assert "DATABASE_OVERLOAD" in types

    ranked = ranker.rank_hypotheses(hypotheses)
    # Highest rank should be deployment or db overload due to supporting evidence counts
    assert ranked[0].score > 0.6


def test_conflict_resolver(mock_sub_agents_output):
    collector = EvidenceCollector()
    resolver = ConflictResolver()
    gen = HypothesisGenerator()

    # Create conflict scenario: DB Overload generated, but metrics list is empty
    conflict_output = mock_sub_agents_output.copy()
    conflict_output["metrics_agent_output"]["anomaly_clusters"] = []

    normalized = collector.collect_and_normalize(conflict_output)
    correlations = CorrelationEngine().find_correlations(normalized)

    hypotheses = gen.generate_hypotheses(normalized, correlations)
    db_hyp = [h for h in hypotheses if h.root_cause_type == "DATABASE_OVERLOAD"][0]
    initial_confidence = db_hyp.confidence

    resolved = resolver.resolve_conflicts(hypotheses, normalized)
    resolved_db_hyp = [h for h in resolved if h.root_cause_type == "DATABASE_OVERLOAD"][0]

    # Confidence should be reduced by 0.15
    assert resolved_db_hyp.confidence == initial_confidence - 0.15
    assert any("Warning: Metrics agent reports no" in s for s in resolved_db_hyp.supporting_evidence)


def test_confidence_engine_and_explanations(mock_sub_agents_output):
    collector = EvidenceCollector()
    gen = HypothesisGenerator()
    ranker = HypothesisRanker()
    engine = ConfidenceEngine()
    expl = ExplanationGenerator()

    normalized = collector.collect_and_normalize(mock_sub_agents_output)
    correlations = CorrelationEngine().find_correlations(normalized)
    hypotheses = gen.generate_hypotheses(normalized, correlations)
    ranked = ranker.rank_hypotheses(hypotheses)

    conf_details = engine.calculate_confidence(ranked, normalized, mock_sub_agents_output)
    assert conf_details["overall_confidence"] > 0.5
    assert conf_details["evidence_quality_score"] > 0.7

    timeline = TimelineAnalyzer().build_cause_effect_timeline(normalized)
    summary = expl.generate_explanations(ranked, timeline)

    assert "most likely root cause is determined to be" in summary.executive_explanation
    assert len(summary.alternative_explanations) >= 1


@pytest.mark.asyncio
async def test_root_cause_agent_end_to_end(mock_sub_agents_output):
    agent = RootCauseAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-rc-1",
        correlation_id="corr-rc-2",
        agent_id="test-rc-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-rc-3",
        severity="SEV1",
        status="active",
        summary="Database slowness issue",
        signals=mock_sub_agents_output
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)

    assert result.success is True
    assert result.output["agent_name"] == "Root Cause Agent"
    assert "BAD_DEPLOYMENT" in [h["root_cause_type"] for h in result.output["alternative_hypotheses"]]
    assert result.output["root_cause"] != ""
    assert len(result.output["timeline_summary"]) == 4


@pytest.mark.asyncio
async def test_root_cause_agent_validation_failures():
    agent = RootCauseAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-rc-1",
        correlation_id="corr-rc-2",
        agent_id="test-rc-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-rc-3",
        severity="SEV1",
        status="active",
        summary="No sub-agents diagnostics"
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)
    assert result.success is False
    assert "upstream sub-agent diagnostic report" in result.reasoning_summary
