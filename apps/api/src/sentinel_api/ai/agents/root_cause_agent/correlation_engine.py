from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(
    "sentinel_api.ai.agents.root_cause_agent.correlation_engine"
)


class CorrelationEngine:
    """Correlates logs, metrics, deployments, and customer reports by service/feature."""

    def find_correlations(
        self, normalized_evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Maps shared technical dimensions (services, features, endpoints)."""
        logger.info("Computing cross-agent dimension correlations")
        correlations: Dict[str, List[Any]] = {
            "services": {},
            "features": {},
            "endpoints": {},
        }

        for ev in normalized_evidence:
            agent = ev["agent"]
            meta = ev["metadata"]

            services = []
            if agent == "DEPLOYMENT":
                services = (
                    meta.get("affected_services")
                    or ([meta.get("service")] if meta.get("service") else [])
                )
            elif agent == "LOG":
                services = [meta.get("service")] if meta.get("service") else []
            elif agent == "METRICS":
                services = [meta.get("service")] if meta.get("service") else []
            elif agent == "REVIEW":
                services = meta.get("affected_services") or []

            for s in services:
                if s:
                    correlations["services"].setdefault(s, []).append(ev)

            features = []
            if agent == "REVIEW":
                features = meta.get("affected_features") or []
                if meta.get("category"):
                    features.append(meta.get("category"))
            elif agent == "DEPLOYMENT":
                if meta.get("change_type"):
                    features.append(meta.get("change_type"))

            for f in features:
                if f:
                    correlations["features"].setdefault(f, []).append(ev)

            endpoints = []
            if agent == "LOG" and meta.get("endpoint"):
                endpoints.append(meta.get("endpoint"))
            elif agent == "REVIEW" and meta.get("endpoints"):
                endpoints.extend(meta.get("endpoints"))

            for ep in endpoints:
                if ep:
                    correlations["endpoints"].setdefault(ep, []).append(ev)

        return correlations
