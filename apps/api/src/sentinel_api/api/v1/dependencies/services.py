from sentinel_api.services.activity import ActivityService
from sentinel_api.services.investigation import InvestigationService
from sentinel_api.services.invitation import InvitationService
from sentinel_api.services.membership import MembershipService
from sentinel_api.services.organization import OrganizationService
from sentinel_api.services.workspace import WorkspaceService
from sentinel_api.services.api_key import ApiKeyService

_investigation_service = InvestigationService()
_organization_service = OrganizationService()
_workspace_service = WorkspaceService()
_membership_service = MembershipService()
_invitation_service = InvitationService()
_activity_service = ActivityService()
_api_key_service = ApiKeyService()


def get_investigation_service() -> InvestigationService:
    """Returns the singleton instance of InvestigationService."""
    return _investigation_service


def get_organization_service() -> OrganizationService:
    """Returns the singleton instance of OrganizationService."""
    return _organization_service


def get_workspace_service() -> WorkspaceService:
    """Returns the singleton instance of WorkspaceService."""
    return _workspace_service


def get_membership_service() -> MembershipService:
    """Returns the singleton instance of MembershipService."""
    return _membership_service


def get_invitation_service() -> InvitationService:
    """Returns the singleton instance of InvitationService."""
    return _invitation_service


def get_activity_service() -> ActivityService:
    """Returns the singleton instance of ActivityService."""
    return _activity_service


def get_api_key_service() -> ApiKeyService:
    """Returns the singleton instance of ApiKeyService."""
    return _api_key_service

