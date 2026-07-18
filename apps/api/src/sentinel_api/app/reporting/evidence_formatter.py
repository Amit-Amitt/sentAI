from typing import Any, Dict
import structlog

from sentinel_api.app.reporting.schemas import EvidenceSummary

logger = structlog.get_logger("sentinel_api.app.reporting.evidence_formatter")


class EvidenceFormatter:
    """Formats raw outputs from specialized agents into structured text evidence logs."""

    def format_evidence(
        self,
        log_output: Dict[str, Any],
        metrics_output: Dict[str, Any],
        deployment_output: Dict[str, Any],
        review_output: Dict[str, Any],
    ) -> EvidenceSummary:
        """Assembles specific strings per evidence diagnostic source."""
        logger.info("Formatting sub-agent evidence logs")

        logs_ev = []
        if log_output and isinstance(log_output, dict):
            findings = log_output.get("findings") or []
            for f in findings:
                logs_ev.append(
                    f"[{f.get('severity')}] {f.get('service')} -"
                    f" {f.get('pattern_name')} ({f.get('endpoint')})"
                )

        metrics_ev = []
        if metrics_output and isinstance(metrics_output, dict):
            findings = (
                metrics_output.get("anomaly_clusters")
                or metrics_output.get("findings")
                or []
            )
            for f in findings:
                metrics_ev.append(
                    f"[{f.get('severity')}] Anomaly on {f.get('service')}:"
                    f" {f.get('metric_name')}"
                )

        deployments_ev = []
        if deployment_output and isinstance(deployment_output, dict):
            findings = (
                deployment_output.get("correlated_events")
                or deployment_output.get("findings")
                or []
            )
            for f in findings:
                deployments_ev.append(
                    f"Change on {f.get('service')} ({f.get('version')}):"
                    f" {f.get('description')} (correlation score:"
                    f" {f.get('correlation_score')})"
                )

        customer_ev = []
        if review_output and isinstance(review_output, dict):
            findings = review_output.get("findings") or []
            for f in findings:
                features = ", ".join(f.get("affected_features", []))
                customer_ev.append(
                    f"[{f.get('severity')}] {f.get('category')}:"
                    f" {f.get('summary')} (affected features: {features})"
                )

        return EvidenceSummary(
            logs=logs_ev,
            metrics=metrics_ev,
            deployments=deployments_ev,
            customer_feedback=customer_ev,
        )
