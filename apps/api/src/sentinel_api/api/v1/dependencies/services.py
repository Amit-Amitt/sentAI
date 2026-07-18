from sentinel_api.services.investigation import InvestigationService

_investigation_service = InvestigationService()


def get_investigation_service() -> InvestigationService:
    """Returns the singleton instance of InvestigationService."""
    return _investigation_service
