from typing import Any, Dict
import structlog

from sentinel_api.app.reporting.schemas import ReportExecutiveSummary

logger = structlog.get_logger("sentinel_api.app.reporting.executive_summary")


class ExecutiveSummaryBuilder:
    """Builds the incident executive summary from sub-agent findings."""

    def build_summary(
        self,
        coordinator_output: Dict[str, Any],
        root_cause_output: Dict[str, Any],
        recommendation_output: Dict[str, Any],
        incident_context: Dict[str, Any],
    ) -> ReportExecutiveSummary:
        """Assembles executive details into a unified summary model."""
        logger.info("Building report executive summary block")

        overview = (
            root_cause_output.get("reasoning")
            or root_cause_output.get("reasoning_summary")
            or incident_context.get("summary")
            or "Incident investigation complete."
        )

        affected_services = (
            recommendation_output.get("metadata", {}).get("affected_services")
            or root_cause_output.get("metadata", {}).get("affected_services")
            or []
        )
        if not affected_services and coordinator_output:
            affected_services = coordinator_output.get("metadata", {}).get(
                "planned_agents", []
            )

        business_impact = (
            recommendation_output.get("business_summary")
            or "Business operations are under review."
        )

        status = incident_context.get("status") or "active"
        investigation_status = f"Investigation completed. Status is '{status}'."
        if recommendation_output:
            action_count = len(
                recommendation_output.get("recommended_actions", [])
            )
            investigation_status += (
                f" Mitigation playbook generated with {action_count} steps."
            )

        return ReportExecutiveSummary(
            incident_overview=overview,
            affected_services=affected_services,
            severity=incident_context.get("severity") or "SEV2",
            business_impact=business_impact,
            investigation_status=investigation_status,
        )
