"""Response schemas for organization, workspace, membership, and invitation endpoints."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """Serialized user within organization context."""

    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    is_active: bool = True


class OrganizationResponse(BaseModel):
    """Serialized organization."""

    id: str
    name: str
    slug: str
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    timezone: Optional[str] = None
    owner_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class OrganizationListResponse(BaseModel):
    """Paginated list of organizations."""

    results: List[OrganizationResponse]
    total: int


class WorkspaceResponse(BaseModel):
    """Serialized workspace."""

    id: str
    name: str
    slug: str
    environment: str
    description: Optional[str] = None
    ai_config: Dict[str, Any] = Field(default_factory=dict)
    incident_retention_days: int = 90
    organization_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class WorkspaceListResponse(BaseModel):
    """List of workspaces within an organization."""

    results: List[WorkspaceResponse]
    total: int


class MembershipResponse(BaseModel):
    """Serialized membership record with embedded user info and scoped workspaces."""

    id: str
    user_id: str
    organization_id: str
    workspace_id: Optional[str] = None
    role: str
    user: Optional[UserResponse] = None
    created_at: Optional[str] = None
    workspaces: List[WorkspaceResponse] = Field(default_factory=list)


class MembershipListResponse(BaseModel):
    """List of memberships within an organization."""

    results: List[MembershipResponse]
    total: int


class InvitationResponse(BaseModel):
    """Serialized invitation."""

    id: str
    email: str
    role: str
    status: str
    organization_id: str
    invited_by: str
    expires_at: Optional[str] = None
    created_at: Optional[str] = None
    workspaces: List[str] = Field(default_factory=list)


class InvitationListResponse(BaseModel):
    """List of invitations within an organization."""

    results: List[InvitationResponse]
    total: int


class MemberActivityResponse(BaseModel):
    """Serialized audit log of member activity."""

    id: str
    organization_id: str
    user_id: Optional[str] = None
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    user: Optional[UserResponse] = None


class MemberActivityListResponse(BaseModel):
    """Paginated list of team member activity logs."""

    results: List[MemberActivityResponse]
    total: int
