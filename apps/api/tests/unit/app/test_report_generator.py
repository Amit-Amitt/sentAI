import pytest
from datetime import datetime, UTC, timedelta
from sentinel_api.app.reporting.report_generator import IncidentReportGenerator
from sentinel_api.app.reporting.executive_summary import ExecutiveSummaryBuilder
from sentinel_api.app.reporting.timeline_builder import TimelineBuilder
from sentinel_api.app.reporting.evidence_formatter import EvidenceFormatter
from sentinel_api.app.reporting.recommendation_formatter import RecommendationFormatter
from sentinel_api.app.reporting.recovery_formatter import RecoveryFormatter
from sentinel_api.app.reporting.confidence_calculator import ConfidenceCalculator
from sentinel_api.app.reporting.schemas import IncidentReport


@pytest.fixture
def mock_all_agent_outputs():
    now = datetime.now(UTC)

    # 1. Coordinator Agent output
    coordinator_out = {
        "success": True,
        "confidence": 0.95,
        "metadata": {
            "execution_start_time": (now - timedelta(minutes=20)).isoformat(),
            "planned_agents": ["payment-service"]
        }
    }

    # 2. Log Agent output
    log_out = {
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
        ]
    }

    # 3. Metrics Agent output
    metrics_out = {
        "success": True,
        "confidence": 0.90,
        "anomaly_clusters": [
            {
                "timestamp": (now - timedelta(minutes=9)).isoformat(),
                "service": "payment-service",
                "metric_name": "db_connection_failures_count",
                "severity": "Critical"
            }
        ]
    }

    # 4. Deployment Agent output
    deployment_out = {
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
        ]
    }

    # 5. Review Agent output
    review_out = {
        "success": True,
        "confidence": 0.80,
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
                "first_report": (now - timedelta(minutes=6)).isoformat()
            }
        }
    }

    # 6. Root Cause Agent output
    rc_out = {
        "success": True,
        "confidence": 0.92,
        "root_cause": "BAD_DEPLOYMENT",
        "reasoning_summary": "Bad deployment v1.3.4 caused database pool timeouts",
        "supporting_evidence": ["Deployment v1.3.4 matches time window", "Log timeouts verified"],
        "alternative_hypotheses": [
            {"root_cause_type": "DATABASE_OVERLOAD", "confidence": 0.65, "description": "High traffic pool overflow"}
        ],
        "metadata": {
            "incident_timestamp": (now - timedelta(minutes=15)).isoformat()
        }
    }

    # 7. Recommendation Agent output
    rec_out = {
        "success": True,
        "confidence": 0.90,
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
        "executive_summary": "Rollback bad deployment to recover checkout service.",
        "technical_summary": "Initiate rollout undo and verify pod ready statuses.",
        "business_summary": "Restoring payment service mitigates checkout blockages.",
        "metadata": {
            "affected_services": ["payment-service"]
        }
    }

    return {
        "coordinator_agent_output": coordinator_out,
        "log_agent_output": log_out,
        "metrics_agent_output": metrics_out,
        "deployment_agent_output": deployment_out,
        "review_agent_output": review_out,
        "root_cause_agent_output": rc_out,
        "recommendation_agent_output": rec_out
    }


def test_executive_summary_builder(mock_all_agent_outputs):
    builder = ExecutiveSummaryBuilder()
    outputs = mock_all_agent_outputs
    
    summary = builder.build_summary(
        outputs["coordinator_agent_output"],
        outputs["root_cause_agent_output"],
        outputs["recommendation_agent_output"],
        {"severity": "SEV1", "status": "active", "summary": "DB timeouts"}
    )
    
    assert summary.severity == "SEV1"
    assert "payment-service" in summary.affected_services
    assert "mitigates checkout blockages" in summary.business_impact


def test_timeline_builder(mock_all_agent_outputs):
    builder = TimelineBuilder()
    outputs = mock_all_agent_outputs
    
    timeline = builder.build_timeline(
        outputs["coordinator_agent_output"],
        outputs["log_agent_output"],
        outputs["metrics_agent_output"],
        outputs["deployment_agent_output"],
        outputs["review_agent_output"],
        outputs["root_cause_agent_output"],
        outputs["recommendation_agent_output"]
    )
    
    # Chronological: Coordinator (20m) -> Deployment (15m) -> Metric (9m) -> Log (8m) -> Review (6m)
    assert len(timeline) >= 6
    assert timeline[0].event_type == "INCIDENT_START"
    assert timeline[1].event_type in ["DEPLOYMENT", "ROOT_CAUSE"]


def test_evidence_formatter(mock_all_agent_outputs):
    formatter = EvidenceFormatter()
    outputs = mock_all_agent_outputs
    
    evidence = formatter.format_evidence(
        outputs["log_agent_output"],
        outputs["metrics_agent_output"],
        outputs["deployment_agent_output"],
        outputs["review_agent_output"]
    )
    
    assert len(evidence.logs) == 1
    assert "Database connection pool timeout error" in evidence.logs[0]
    assert len(evidence.metrics) == 1
    assert "db_connection_failures_count" in evidence.metrics[0]


def test_recommendation_formatter(mock_all_agent_outputs):
    formatter = RecommendationFormatter()
    outputs = mock_all_agent_outputs
    
    sec = formatter.format_recommendations(outputs["recommendation_agent_output"])
    
    assert len(sec.immediate_actions) == 1
    assert sec.immediate_actions[0]["title"] == "Rollback payment-service Deployment"
    assert sec.risk == "Medium"
    assert sec.priority == "Critical"


def test_confidence_calculator(mock_all_agent_outputs):
    calc = ConfidenceCalculator()
    outputs = mock_all_agent_outputs
    
    conf = calc.calculate(
        outputs["coordinator_agent_output"],
        outputs["log_agent_output"],
        outputs["metrics_agent_output"],
        outputs["deployment_agent_output"],
        outputs["review_agent_output"],
        outputs["root_cause_agent_output"],
        outputs["recommendation_agent_output"]
    )
    
    assert conf.coverage_score == 1.0
    assert conf.overall_confidence == 0.92
    assert conf.evidence_quality == 0.88  # Average of 0.85, 0.90, 0.95, 0.80


def test_report_generator_end_to_end(mock_all_agent_outputs):
    generator = IncidentReportGenerator()
    outputs = mock_all_agent_outputs
    
    incident_ctx = {
        "incident_id": "INC-483",
        "severity": "SEV1",
        "status": "active",
        "created_at": datetime.now(UTC).isoformat()
    }
    
    report = generator.generate_report(outputs, incident_ctx)
    assert isinstance(report, IncidentReport)
    assert report.metadata.incident_id == "INC-483"
    assert len(report.timeline) >= 6
    
    # Check JSON export
    json_str = generator.export_report(report, format="json")
    assert "INC-483" in json_str
    
    # Check Markdown export
    md_str = generator.export_report(report, format="markdown")
    assert "# Sentinel AI Incident Report: INC-483" in md_str
    assert "## 1. Executive Summary" in md_str
    assert "## 2. Chronological Timeline" in md_str
    assert "## 4. Root Cause Deduction" in md_str
