import pytest
from sentinel_api.ai.agents.log_agent import LogAgent
from sentinel_api.ai.agents.log_agent.parser import LogParser
from sentinel_api.ai.agents.log_agent.extractor import MetadataExtractor
from sentinel_api.ai.agents.log_agent.pattern_detector import PatternDetector
from sentinel_api.ai.agents.log_agent.severity import SeverityClassifier
from sentinel_api.ai.agents.log_agent.anomaly_detector import AnomalyDetector
from sentinel_api.ai.agents.log_agent.summarizer import LogSummarizer
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)


@pytest.fixture
def sample_json_logs():
    return (
        '{"timestamp": "2026-07-17T23:40:00Z", "level": "error", "message": "Failed to connect to database at db.prod:5432. Timeout reached.", "service": "user-auth", "component": "db-client", "request_id": "req-101"}\n'
        '{"timestamp": "2026-07-17T23:40:05Z", "level": "info", "message": "User authenticated successfully", "service": "user-auth", "component": "auth-engine", "user_id": "user-999"}\n'
        '{"timestamp": "2026-07-17T23:40:10Z", "level": "error", "message": "Failed to connect to database at db.prod:5432. Timeout reached.", "service": "user-auth", "component": "db-client", "request_id": "req-102"}\n'
    )


@pytest.fixture
def sample_mixed_logs():
    return (
        "2026-07-17T23:40:15Z ERROR gateway-service [ingress] : HTTP 502 Bad Gateway for upstream /api/v1/auth (request_id=req-201)\n"
        "2026-07-17T23:40:20Z WARNING gateway-service : High latency detected on downstream peer host=peer-node-1\n"
        "Unstructured raw dump containing Exception in thread 'main' java.lang.OutOfMemoryError: Java heap space on 2026-07-17 23:40:25\n"
    )


def test_log_parser_json(sample_json_logs):
    parser = LogParser()
    parsed = parser.parse_logs(sample_json_logs)

    assert len(parsed) == 3
    assert parsed[0]["level"] == "ERROR"
    assert parsed[0]["service"] == "user-auth"
    assert parsed[0]["component"] == "db-client"
    assert parsed[0]["message"] == "Failed to connect to database at db.prod:5432. Timeout reached."
    assert parsed[0]["metadata"]["request_id"] == "req-101"


def test_log_parser_mixed(sample_mixed_logs):
    parser = LogParser()
    parsed = parser.parse_logs(sample_mixed_logs)

    assert len(parsed) == 3
    # First line parsed via regex
    assert parsed[0]["level"] == "ERROR"
    assert parsed[0]["service"] == "gateway-service"
    assert parsed[0]["component"] == "ingress"
    assert "HTTP 502 Bad Gateway" in parsed[0]["message"]

    # Third line parsed via fallback (java.lang.OutOfMemoryError)
    assert parsed[2]["level"] == "INFO"  # No level pattern matches standard regex directly in fallback, defaults to INFO or WARN
    assert "OutOfMemoryError" in parsed[2]["message"]


def test_metadata_extractor(sample_json_logs, sample_mixed_logs):
    parser = LogParser()
    extractor = MetadataExtractor()

    parsed_json = parser.parse_logs(sample_json_logs)
    parsed_mixed = parser.parse_logs(sample_mixed_logs)

    meta_json = extractor.extract_metadata(parsed_json)
    assert "user-auth" in meta_json["services"]
    assert "db-client" in meta_json["components"]
    assert "req-101" in meta_json["request_ids"]
    assert "user-999" in meta_json["user_ids"]

    meta_mixed = extractor.extract_metadata(parsed_mixed)
    assert "gateway-service" in meta_mixed["services"]
    assert "peer-node-1" in meta_mixed["hosts"]
    assert "req-201" in meta_mixed["request_ids"]


def test_pattern_detector(sample_json_logs):
    parser = LogParser()
    detector = PatternDetector()

    parsed = parser.parse_logs(sample_json_logs)
    findings = detector.detect_patterns(parsed)

    # Output clusters the 2 identical DB errors
    # (Note: we had 2 error lines and 1 info line. Only warnings/errors are clustered)
    assert len(findings) == 1
    f = findings[0]
    assert f["category"] == "TIMEOUT"  # matches connection/timeout
    assert f["occurrences"] == 2
    assert "db-client" in f["sample_log"]


def test_severity_classifier():
    classifier = SeverityClassifier()

    assert classifier.classify("MEMORY", 1, "CRITICAL") == "Critical"
    assert classifier.classify("CONNECTION", 3, "ERROR") == "High"
    assert classifier.classify("HTTP_5XX", 12, "ERROR") == "High"
    assert classifier.classify("HTTP_4XX", 5, "ERROR") == "Medium"
    assert classifier.classify("AUTHENTICATION", 1, "WARN") == "Medium"
    assert classifier.classify("GENERIC_WARN", 2, "WARN") == "Low"


def test_anomaly_detector(sample_json_logs):
    parser = LogParser()
    detector = PatternDetector()
    anomaly_detector = AnomalyDetector()

    parsed = parser.parse_logs(sample_json_logs)
    findings = detector.detect_patterns(parsed)
    anomalies = anomaly_detector.detect_anomalies(parsed, findings)

    # 2 DB connection errors represent 66.6% of 3 logs total (exceeds high frequency >30% ratio)
    assert len(anomalies) >= 1
    assert any(a["type"] == "HIGH_FREQUENCY_FAILURE" for a in anomalies)


def test_summarizer(sample_json_logs):
    parser = LogParser()
    detector = PatternDetector()
    extractor = MetadataExtractor()
    anomaly_detector = AnomalyDetector()
    summarizer = LogSummarizer()

    parsed = parser.parse_logs(sample_json_logs)
    metadata = extractor.extract_metadata(parsed)
    findings = detector.detect_patterns(parsed)
    # Mock severity mappings to build structured input findings
    classified_findings = []
    for f in findings:
        classified_findings.append({
            "template": f["template"],
            "category": f["category"],
            "severity": "High",
            "occurrences": f["occurrences"]
        })
    anomalies = anomaly_detector.detect_anomalies(parsed, findings)

    summary = summarizer.summarize(classified_findings, anomalies, metadata, len(parsed))
    assert "user-auth" in summary.short_summary
    assert "TIMEOUT" in summary.key_observations[1]
    assert any("Upstream" in c for c in summary.potential_contributors)


@pytest.mark.asyncio
async def test_log_agent_end_to_end(sample_json_logs):
    agent = LogAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-log-agent-1",
        correlation_id="corr-log-agent-2",
        agent_id="test-log-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-log-agent-3",
        severity="SEV2",
        status="active",
        summary="High database CPU load",
        signals={"raw_logs": sample_json_logs}
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)

    assert result.success is True
    assert result.output["agent_name"] == "Log Agent"
    assert result.output["status"] == "SUCCESS"
    assert len(result.output["findings"]) == 1
    assert result.output["findings"][0]["category"] == "TIMEOUT"
    assert result.output["findings"][0]["occurrences"] == 2
    assert "user-auth" in result.output["metadata"]["services"]
    assert result.output["statistics"]["lines_parsed"] == 3
    assert result.confidence > 0.5


@pytest.mark.asyncio
async def test_log_agent_validation_failures():
    agent = LogAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-log-agent-1",
        correlation_id="corr-log-agent-2",
        agent_id="test-log-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-log-agent-3",
        severity="SEV2",
        status="active",
        summary="No logs context"
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    # Should fail validation because logs is missing in both signals and inputs
    result = await agent.execute(request, config)
    assert result.success is False
    assert "Log data is missing" in result.reasoning_summary
