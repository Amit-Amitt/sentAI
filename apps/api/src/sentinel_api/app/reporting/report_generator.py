from typing import Any, Dict
import structlog

from sentinel_api.app.reporting.confidence_calculator import (
    ConfidenceCalculator,
)
from sentinel_api.app.reporting.evidence_formatter import EvidenceFormatter
from sentinel_api.app.reporting.executive_summary import ExecutiveSummaryBuilder
from sentinel_api.app.reporting.json_exporter import JsonExporter
from sentinel_api.app.reporting.markdown_exporter import MarkdownExporter
from sentinel_api.app.reporting.recovery_formatter import RecoveryFormatter
from sentinel_api.app.reporting.recommendation_formatter import (
    RecommendationFormatter,
)
from sentinel_api.app.reporting.schemas import (
    IncidentReport,
    ReportMetadata,
    RootCauseSection,
)
from sentinel_api.app.reporting.timeline_builder import TimelineBuilder
from sentinel_api.app.reporting.utils import get_current_utc_timestamp

logger = structlog.get_logger("sentinel_api.app.reporting.report_generator")


class IncidentReportGenerator:
    """Consolidates diagnostic data from multiple SRE sub-agents into a single unified incident report."""

    def __init__(self) -> None:
        self.executive_builder = ExecutiveSummaryBuilder()
        self.timeline_builder = TimelineBuilder()
        self.evidence_formatter = EvidenceFormatter()
        self.recommendation_formatter = RecommendationFormatter()
        self.recovery_formatter = RecoveryFormatter()
        self.confidence_calculator = ConfidenceCalculator()
        self.json_exporter = JsonExporter()
        self.markdown_exporter = MarkdownExporter()

    def generate_report(
        self, agent_outputs: Dict[str, Any], incident_context: Dict[str, Any]
    ) -> IncidentReport:
        """Combines and normalizes all AI agent execution outputs into a structured IncidentReport."""
        logger.info("Generating incident report from agent outputs")

        # 1. Resolve agent outputs
        coord = agent_outputs.get("coordinator_agent_output") or {}
        logs = agent_outputs.get("log_agent_output") or {}
        metrics = agent_outputs.get("metrics_agent_output") or {}
        deploy = agent_outputs.get("deployment_agent_output") or {}
        review = agent_outputs.get("review_agent_output") or {}
        rc = agent_outputs.get("root_cause_agent_output") or {}
        rec = agent_outputs.get("recommendation_agent_output") or {}

        # 2. Build metadata
        svc_list = (
            rec.get("metadata", {}).get("affected_services")
            or rc.get("metadata", {}).get("affected_services")
            or []
        )
        if isinstance(svc_list, str):
            svc_list = [svc_list]

        metadata = ReportMetadata(
            incident_id=incident_context.get("incident_id") or "INC-UNKNOWN",
            severity=incident_context.get("severity") or "SEV2",
            status=incident_context.get("status") or "active",
            created_at=incident_context.get("created_at")
            or get_current_utc_timestamp(),
            owner=(
                "sre-team"
                if not svc_list
                else f"team-{svc_list[0]}"
            ),
            affected_services=svc_list,
        )

        # 3. Formulate sections
        exec_summary = self.executive_builder.build_summary(
            coord, rc, rec, incident_context
        )
        timeline = self.timeline_builder.build_timeline(
            coord, logs, metrics, deploy, review, rc, rec
        )
        evidence = self.evidence_formatter.format_evidence(
            logs, metrics, deploy, review
        )

        root_cause = RootCauseSection(
            primary_root_cause=rc.get("root_cause")
            or "Unknown root cause diagnosis",
            supporting_evidence=rc.get("supporting_evidence") or [],
            alternative_hypotheses=rc.get("alternative_hypotheses") or [],
            confidence=float(rc.get("confidence") or 0.85),
        )

        recommendations = self.recommendation_formatter.format_recommendations(
            rec
        )
        recovery_plan = self.recovery_formatter.format_recovery_plan(rec)
        confidence = self.confidence_calculator.calculate(
            coord, logs, metrics, deploy, review, rc, rec
        )

        return IncidentReport(
            metadata=metadata,
            executive_summary=exec_summary,
            timeline=timeline,
            evidence=evidence,
            root_cause=root_cause,
            recommendations=recommendations,
            recovery_plan=recovery_plan,
            confidence=confidence,
            raw_metadata=agent_outputs,
        )

    def export_report(self, report: IncidentReport, format: str = "json") -> str:
        """Serializes the IncidentReport model to either JSON or Markdown format."""
        logger.info(f"Exporting incident report in format: {format}")
        if format.lower() == "markdown":
            return self.markdown_exporter.export(report)
        return self.json_exporter.export(report)
