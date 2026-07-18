from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(
    "sentinel_api.ai.agents.root_cause_agent.evidence_collector"
)


class EvidenceCollector:
    """Collects and standardizes raw output formats from upstream diagnostic agents."""

    def collect_and_normalize(
        self, signals: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parses sub-agent payloads to output lists of standardized evidence points."""
        logger.info("Normalizing evidence maps from sub-agents")
        normalized: List[Dict[str, Any]] = []

        # 1. Log Agent
        logs_output = signals.get("log_agent_output") or signals.get("log_agent")
        if logs_output and isinstance(logs_output, dict):
            findings = logs_output.get("findings") or []
            confidence = logs_output.get("confidence", 0.8)
            for f in findings:
                normalized.append(
                    {
                        "timestamp": (
                            f.get("timestamp")
                            or logs_output.get("metadata", {}).get(
                                "incident_timestamp"
                            )
                            or ""
                        ),
                        "agent": "LOG",
                        "description": (
                            f.get("pattern_name")
                            or f.get("description")
                            or "Log error pattern detected"
                        ),
                        "severity": f.get("severity") or "High",
                        "confidence": f.get("confidence") or confidence,
                        "metadata": f,
                    }
                )

        # 2. Metrics Agent
        metrics_output = signals.get("metrics_agent_output") or signals.get(
            "metrics_agent"
        )
        if metrics_output and isinstance(metrics_output, dict):
            findings = (
                metrics_output.get("anomaly_clusters")
                or metrics_output.get("findings")
                or []
            )
            confidence = metrics_output.get("confidence", 0.8)
            for f in findings:
                normalized.append(
                    {
                        "timestamp": (
                            f.get("timestamp")
                            or metrics_output.get("metadata", {}).get(
                                "incident_timestamp"
                            )
                            or ""
                        ),
                        "agent": "METRICS",
                        "description": (
                            f.get("metric_name")
                            or f.get("description")
                            or "Metric anomaly detected"
                        ),
                        "severity": f.get("severity") or "High",
                        "confidence": f.get("confidence") or confidence,
                        "metadata": f,
                    }
                )

        # 3. Deployment Agent
        dep_output = signals.get("deployment_agent_output") or signals.get(
            "deployment_agent"
        )
        if dep_output and isinstance(dep_output, dict):
            findings = dep_output.get("correlated_events") or dep_output.get("findings") or []
            confidence = dep_output.get("confidence", 0.8)
            for f in findings:
                normalized.append(
                    {
                        "timestamp": (
                            f.get("timestamp")
                            or dep_output.get("metadata", {}).get(
                                "incident_timestamp"
                            )
                            or ""
                        ),
                        "agent": "DEPLOYMENT",
                        "description": (
                            f.get("description")
                            or f.get("summary")
                            or "Deployment correlated with incident"
                        ),
                        "severity": (
                            "High"
                            if f.get("correlation_score", 0) >= 0.7
                            else "Medium"
                        ),
                        "confidence": f.get("confidence") or confidence,
                        "metadata": f,
                    }
                )

        # 4. Review Agent
        rev_output = signals.get("review_agent_output") or signals.get(
            "review_agent"
        )
        if rev_output and isinstance(rev_output, dict):
            findings = rev_output.get("findings") or []
            confidence = rev_output.get("confidence", 0.8)
            for f in findings:
                normalized.append(
                    {
                        "timestamp": (
                            rev_output.get("metadata", {},)
                            .get("timeline_stats", {})
                            .get("first_report")
                            or ""
                        ),
                        "agent": "REVIEW",
                        "description": (
                            f.get("summary")
                            or "User reports feedback ticket cluster"
                        ),
                        "severity": f.get("severity") or "Medium",
                        "confidence": f.get("confidence") or confidence,
                        "metadata": f,
                    }
                )

        normalized.sort(
            key=lambda x: x["timestamp"] or "9999-12-31T23:59:59"
        )
        return normalized
