import structlog

from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.schemas.models import IncidentContext

logger = structlog.get_logger("sentinel_api.ai.agents.coordinator.validator")


class IncidentValidator:
    """Validates incoming IncidentContext structures to ensure logical integrity."""

    def validate(self, incident: IncidentContext) -> None:
        """Validates crucial fields of the IncidentContext.

        Raises:
            AgentException if the context structure is invalid.
        """
        logger.info("Validating IncidentContext", incident_id=incident.incident_id)

        if not incident.incident_id:
            logger.error("IncidentContext validation failed: Missing incident_id")
            raise AgentException("Incident ID is missing in context.")

        if not incident.severity:
            logger.error("IncidentContext validation failed: Missing severity")
            raise AgentException("Incident severity is missing in context.")

        if not incident.status:
            logger.error("IncidentContext validation failed: Missing status")
            raise AgentException("Incident status is missing in context.")

        if not incident.summary or not incident.summary.strip():
            logger.error("IncidentContext validation failed: Empty summary")
            raise AgentException("Incident summary cannot be empty.")
