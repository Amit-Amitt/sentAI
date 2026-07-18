import time
from typing import Any, Dict
import structlog

from sentinel_api.ai.agents.log_agent.anomaly_detector import AnomalyDetector
from sentinel_api.ai.agents.log_agent.extractor import MetadataExtractor
from sentinel_api.ai.agents.log_agent.parser import LogParser
from sentinel_api.ai.agents.log_agent.pattern_detector import PatternDetector
from sentinel_api.ai.agents.log_agent.schemas import (
    LogAgentOutput,
    LogFinding,
    LogProcessingStats,
)
from sentinel_api.ai.agents.log_agent.severity import SeverityClassifier
from sentinel_api.ai.agents.log_agent.summarizer import LogSummarizer
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.runtime.agent import BaseAgent
from sentinel_api.ai.schemas.models import AgentRequest

logger = structlog.get_logger("sentinel_api.ai.agents.log_agent.log_agent")


class LogAgent(BaseAgent):
    """Specialized agent responsible for analyzing logs and extracting evidence."""

    def __init__(self) -> None:
        super().__init__(name="Log Agent")
        self.parser = LogParser()
        self.extractor = MetadataExtractor()
        self.pattern_detector = PatternDetector()
        self.severity_classifier = SeverityClassifier()
        self.anomaly_detector = AnomalyDetector()
        self.summarizer = LogSummarizer()

    def validate(self, request: AgentRequest) -> None:
        """Ensures that log payload inputs are present in incoming request signals or inputs."""
        super().validate(request)

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        logs = (
            signals.get("logs")
            or signals.get("raw_logs")
            or inputs.get("logs")
            or inputs.get("raw_logs")
        )

        if not logs or not str(logs).strip():
            raise AgentException("Log data is missing or empty in signals/inputs.")

    async def _run(
        self, request: AgentRequest, config: ModelConfig
    ) -> Dict[str, Any]:
        """Runs the parsing, metadata, pattern grouping, severity and summarization loops."""
        start_time = time.perf_counter()

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        raw_logs = str(
            signals.get("logs")
            or signals.get("raw_logs")
            or inputs.get("logs")
            or inputs.get("raw_logs")
        )

        # 1. Parse raw log lines
        parsed_logs = self.parser.parse_logs(raw_logs)
        total_parsed = len(parsed_logs)

        # 2. Gather environment metadata
        metadata = self.extractor.extract_metadata(parsed_logs)

        # 3. Detect patterns/clusters
        pattern_groups = self.pattern_detector.detect_patterns(parsed_logs)

        # 4. Classify severities and build finding entities
        findings: list[LogFinding] = []
        for pg in pattern_groups:
            severity = self.severity_classifier.classify(
                category=pg["category"],
                occurrences=pg["occurrences"],
                max_level=pg["level"],
            )

            # Heuristically evaluate confidence
            base_conf = 0.6
            if pg["category"] not in ["GENERIC_ERROR", "GENERIC_WARN"]:
                base_conf += 0.2
            base_conf += min(0.2, pg["occurrences"] / 50.0)
            confidence = min(1.0, base_conf)

            findings.append(
                LogFinding(
                    category=pg["category"],
                    severity=severity,
                    confidence=confidence,
                    summary=f"Clustered errors matching template: '{pg['template']}'",
                    occurrences=pg["occurrences"],
                    sample_log=pg["sample_log"],
                    timestamp_start=pg["timestamp_start"],
                    timestamp_end=pg["timestamp_end"],
                )
            )

        # 5. Identify statistical anomalies
        anomalies = self.anomaly_detector.detect_anomalies(
            parsed_logs, pattern_groups
        )

        # 6. Compose log summary block
        summary = self.summarizer.summarize(
            findings=[f.model_dump() for f in findings],
            anomalies=anomalies,
            metadata=metadata,
            total_parsed=total_parsed,
        )

        # 7. Calculate aggregate confidence
        overall_confidence = 0.8
        if findings:
            overall_confidence = round(
                sum(f.confidence for f in findings) / len(findings), 2
            )

        # 8. Record processing statistics
        duration_ms = (time.perf_counter() - start_time) * 1000
        statistics = LogProcessingStats(
            lines_parsed=total_parsed,
            anomalies_detected=len(anomalies),
            error_clusters_count=len(findings),
            execution_time_ms=duration_ms,
        )

        output = LogAgentOutput(
            agent_name=self.name,
            execution_time_ms=duration_ms,
            status="SUCCESS" if total_parsed > 0 else "PARTIAL_SUCCESS",
            confidence=overall_confidence,
            findings=findings,
            summary=summary,
            metadata=metadata,
            statistics=statistics,
        )

        result_dict = output.model_dump()
        result_dict["reasoning_summary"] = summary.short_summary
        return result_dict
