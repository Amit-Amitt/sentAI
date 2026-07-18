from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(
    "sentinel_api.ai.agents.recommendation_agent.summary_generator"
)


class SummaryGenerator:
    """Generates narrative summaries covering business, executive, and technical aspects."""

    def generate_summaries(
        self,
        root_cause: str,
        incident_priority: str,
        affected_services: List[str],
        actions: List[Any],
    ) -> Dict[str, str]:
        """Constructs plain text summaries for dashboard presentation and ticketing."""
        logger.info("Generating incident recovery plan summaries")
        svc = affected_services[0] if affected_services else "unknown-service"

        exec_sum = (
            f"Mitigation plan initiated for {svc} (Priority: {incident_priority})."
            f" Diagnosed root cause: '{root_cause}'. The recommended action is"
            f" to perform a rollback/restart of the affected systems to restore"
            f" service availability."
        )

        tech_sum = (
            f"Technical response playbook involves {len(actions)} steps."
            f" Primary action is to address '{root_cause}' on {svc}."
            f" Execution involves validating current revision status and"
            f" issuing rollback commands."
        )

        biz_sum = (
            f"Executing this plan has a {incident_priority} priority."
            f" Successfully deploying the recommendations will restore core"
            f" checkout/auth conversion pathways, minimizing further customer"
            f" conversion drops."
        )

        return {
            "executive_summary": exec_sum,
            "technical_summary": tech_sum,
            "business_summary": biz_sum,
        }
