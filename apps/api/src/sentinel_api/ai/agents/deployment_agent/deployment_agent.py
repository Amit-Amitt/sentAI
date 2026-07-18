import time
from typing import Any, Dict
import structlog

from sentinel_api.ai.agents.deployment_agent.change_detector import ChangeDetector
from sentinel_api.ai.agents.deployment_agent.config_change_detector import (
    ConfigChangeDetector,
)
from sentinel_api.ai.agents.deployment_agent.correlation_engine import (
    CorrelationEngine,
)
from sentinel_api.ai.agents.deployment_agent.deployment_parser import (
    DeploymentParser,
)
from sentinel_api.ai.agents.deployment_agent.feature_flag_analyzer import (
    FeatureFlagAnalyzer,
)
from sentinel_api.ai.agents.deployment_agent.release_analyzer import ReleaseAnalyzer
from sentinel_api.ai.agents.deployment_agent.rollback_detector import (
    RollbackDetector,
)
from sentinel_api.ai.agents.deployment_agent.schemas import (
    DeploymentAgentOutput,
    DeploymentSummary,
)
from sentinel_api.ai.agents.deployment_agent.timeline_builder import (
    TimelineBuilder,
)
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.runtime.agent import BaseAgent
from sentinel_api.ai.schemas.models import AgentRequest

logger = structlog.get_logger("sentinel_api.ai.agents.deployment_agent.deployment_agent")


class DeploymentAgent(BaseAgent):
    """Audits CI/CD and configuration shifts relative to incident timestamps."""

    def __init__(self) -> None:
        super().__init__(name="Deployment Agent")
        self.parser = DeploymentParser()
        self.timeline_builder = TimelineBuilder()
        self.change_detector = ChangeDetector()
        self.config_change_detector = ConfigChangeDetector()
        self.flag_analyzer = FeatureFlagAnalyzer()
        self.rollback_detector = RollbackDetector()
        self.release_analyzer = ReleaseAnalyzer()
        self.correlation_engine = CorrelationEngine()

    def validate(self, request: AgentRequest) -> None:
        """Verifies deployment feed presence in signals/inputs."""
        super().validate(request)

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        deployments = (
            signals.get("deployments")
            or signals.get("raw_deployments")
            or inputs.get("deployments")
            or inputs.get("raw_deployments")
        )

        if not deployments:
            raise AgentException(
                "Deployment data is missing or empty in signals/inputs."
            )

    async def _run(
        self, request: AgentRequest, config: ModelConfig
    ) -> Dict[str, Any]:
        """Triage, timeline build, risk analyze, and correlate deployment telemetry."""
        start_time = time.perf_counter()

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        raw_deployments = (
            signals.get("deployments")
            or signals.get("raw_deployments")
            or inputs.get("deployments")
            or inputs.get("raw_deployments")
        )

        # 1. Parser
        events = self.parser.parse(raw_deployments)

        # 2. Timeline
        incident_time_str = (
            signals.get("incident_time")
            or inputs.get("incident_time")
            or request.execution_context.timestamp.isoformat()
        )
        timeline = self.timeline_builder.build_timeline(
            events, incident_time_str
        )

        # 3. Classify
        classified = self.change_detector.detect_changes(events)

        # 4. Details
        configs = self.config_change_detector.analyze_config_changes(
            classified["CONFIG"]
        )
        flags = self.flag_analyzer.analyze_flags(classified["FLAG"])
        rollbacks = self.rollback_detector.detect_rollbacks(events)
        release_risks = self.release_analyzer.analyze_releases(events)

        # 5. Correlate
        findings = self.correlation_engine.correlate(
            events, incident_time_str, release_risks
        )

        # 6. Summary compilation
        short_summary = (
            f"Deployment analysis completed. Evaluated {len(events)} events. "
        )
        if findings:
            high = [f for f in findings if f.correlation_score >= 0.7]
            short_summary += (
                f"Identified {len(findings)} correlated changes, with"
                f" {len(high)} showing high correlation."
            )
        else:
            short_summary += (
                "No deployments strongly correlated with the incident timeline."
            )

        timeline_summary = [t.description for t in timeline]

        detected_risks = []
        for r in release_risks.values():
            detected_risks.extend(r["reasons"])
        for c in configs:
            if c["is_secret"]:
                detected_risks.append(f"Secret updated on service '{c['service']}'")
        for f in flags:
            if f["risk_level"] == "High":
                detected_risks.append(
                    f"High risk feature flag toggle: {f['description']}"
                )
        for rb in rollbacks:
            detected_risks.append(f"Deployment instability: {rb['description']}")

        key_changes = []
        for ev in events:
            key_changes.append(
                f"[{ev.change_type}] {ev.service} ({ev.version}) status:"
                f" {ev.status}"
            )

        potential_contributors = []
        for f in findings:
            if f.correlation_score >= 0.7:
                potential_contributors.append(
                    f"Deployment of {', '.join(f.affected_services)} ({f.version})"
                    f" shortly before incident onset (Correlation:"
                    f" {f.correlation_score})."
                )
        if not potential_contributors:
            potential_contributors.append("No highly correlated deployments identified.")

        summary = DeploymentSummary(
            short_summary=short_summary,
            timeline_summary=timeline_summary,
            detected_risks=list(set(detected_risks)),
            key_changes=key_changes,
            potential_contributors=potential_contributors,
        )

        confidence = 0.85
        if findings:
            confidence = findings[0].confidence

        duration_ms = (time.perf_counter() - start_time) * 1000

        output = DeploymentAgentOutput(
            agent_name=self.name,
            execution_time_ms=duration_ms,
            status="SUCCESS" if events else "PARTIAL_SUCCESS",
            confidence=confidence,
            findings=findings,
            deployment_timeline=timeline,
            correlated_events=findings,
            summary=summary,
            metadata={
                "events_count": len(events),
                "incident_timestamp": incident_time_str or "",
                "config_changes_count": len(configs),
                "flag_changes_count": len(flags),
                "rollbacks_count": len(rollbacks),
            },
        )

        result_dict = output.model_dump()
        result_dict["reasoning_summary"] = summary.short_summary
        return result_dict
