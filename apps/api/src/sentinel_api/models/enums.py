"""Enumerations for multi-tenant organization and workspace system."""

from enum import Enum


class MemberRole(str, Enum):
    """Roles available within an organization."""

    OWNER = "owner"
    ADMIN = "admin"
    ENGINEER = "engineer"
    VIEWER = "viewer"


class InvitationStatus(str, Enum):
    """Lifecycle states for team invitations."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class WorkspaceEnvironment(str, Enum):
    """Environment classification for workspaces."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Permission(str, Enum):
    """Granular permission actions within the platform."""

    CREATE_WORKSPACE = "create_workspace"
    DELETE_WORKSPACE = "delete_workspace"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_BILLING = "manage_billing"
    RUN_AI_ANALYSIS = "run_ai_analysis"
    VIEW_REPORTS = "view_reports"
    MANAGE_API_KEYS = "manage_api_keys"
    MANAGE_INTEGRATIONS = "manage_integrations"


# Role → Permission mapping (additive hierarchy)
ROLE_PERMISSIONS: dict[MemberRole, set[Permission]] = {
    MemberRole.VIEWER: {
        Permission.VIEW_REPORTS,
    },
    MemberRole.ENGINEER: {
        Permission.VIEW_REPORTS,
        Permission.RUN_AI_ANALYSIS,
    },
    MemberRole.ADMIN: {
        Permission.VIEW_REPORTS,
        Permission.RUN_AI_ANALYSIS,
        Permission.CREATE_WORKSPACE,
        Permission.DELETE_WORKSPACE,
        Permission.MANAGE_MEMBERS,
        Permission.MANAGE_API_KEYS,
        Permission.MANAGE_INTEGRATIONS,
    },
    MemberRole.OWNER: {
        Permission.VIEW_REPORTS,
        Permission.RUN_AI_ANALYSIS,
        Permission.CREATE_WORKSPACE,
        Permission.DELETE_WORKSPACE,
        Permission.MANAGE_MEMBERS,
        Permission.MANAGE_BILLING,
        Permission.MANAGE_API_KEYS,
        Permission.MANAGE_INTEGRATIONS,
    },
}


def has_permission(role: MemberRole, permission: Permission) -> bool:
    """Check if a given role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())
