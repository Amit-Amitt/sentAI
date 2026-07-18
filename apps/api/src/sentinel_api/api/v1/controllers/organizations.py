"""Controller handling mapping logic for organization & membership endpoints."""

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.responses.organization import (
    InvitationListResponse,
    InvitationResponse,
    MembershipListResponse,
    MembershipResponse,
    OrganizationListResponse,
    OrganizationResponse,
    UserResponse,
)
from sentinel_api.api.v1.validators.invitation import CreateInvitationRequest
from sentinel_api.api.v1.validators.membership import (
    AddMemberRequest,
    UpdateMemberRoleRequest,
)
from sentinel_api.api.v1.validators.organization import (
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
)
from sentinel_api.services.invitation import InvitationService
from sentinel_api.services.membership import MembershipService
from sentinel_api.services.organization import OrganizationService


def _serialize_org(org) -> OrganizationResponse:
    """Converts an Organization model to response schema."""
    return OrganizationResponse(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        logo_url=org.logo_url,
        industry=org.industry,
        region=org.region,
        timezone=org.timezone,
        owner_id=str(org.owner_id),
        created_at=org.created_at.isoformat() if org.created_at else None,
        updated_at=org.updated_at.isoformat() if org.updated_at else None,
    )


def _serialize_membership(m) -> MembershipResponse:
    """Converts a Membership model to response schema with embedded user."""
    user_resp = None
    if m.user:
        user_resp = UserResponse(
            id=str(m.user.id),
            email=m.user.email,
            full_name=m.user.full_name,
            avatar_url=m.user.avatar_url,
            is_active=m.user.is_active,
        )
    return MembershipResponse(
        id=str(m.id),
        user_id=str(m.user_id),
        organization_id=str(m.organization_id),
        workspace_id=str(m.workspace_id) if m.workspace_id else None,
        role=m.role,
        user=user_resp,
        created_at=m.created_at.isoformat() if m.created_at else None,
    )


def _serialize_invitation(inv) -> InvitationResponse:
    """Converts an Invitation model to response schema."""
    return InvitationResponse(
        id=str(inv.id),
        email=inv.email,
        role=inv.role,
        status=inv.status,
        organization_id=str(inv.organization_id),
        invited_by=str(inv.invited_by),
        expires_at=inv.expires_at.isoformat() if inv.expires_at else None,
        created_at=inv.created_at.isoformat() if inv.created_at else None,
    )


class OrganizationsController:
    """Controller for organization, membership, and invitation operations."""

    def __init__(
        self,
        org_service: OrganizationService,
        membership_service: MembershipService,
        invitation_service: InvitationService,
    ) -> None:
        self.org_service = org_service
        self.membership_service = membership_service
        self.invitation_service = invitation_service

    # ── Organization CRUD ─────────────────────────────────────

    async def create(
        self,
        db: AsyncSession,
        payload: CreateOrganizationRequest,
        user_id: uuid.UUID,
    ) -> OrganizationResponse:
        org = await self.org_service.create_organization(
            db=db,
            name=payload.name,
            slug=payload.slug,
            owner_id=user_id,
            industry=payload.industry,
            region=payload.region,
            timezone=payload.timezone or "UTC",
        )
        return _serialize_org(org)

    async def get(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> OrganizationResponse:
        org = await self.org_service.get_organization(db, org_id)
        return _serialize_org(org)

    async def list_all(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> OrganizationListResponse:
        orgs = await self.org_service.list_user_organizations(db, user_id)
        return OrganizationListResponse(
            results=[_serialize_org(o) for o in orgs],
            total=len(orgs),
        )

    async def update(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        payload: UpdateOrganizationRequest,
    ) -> OrganizationResponse:
        update_data = payload.model_dump(exclude_none=True)
        org = await self.org_service.update_organization(db, org_id, **update_data)
        return _serialize_org(org)

    async def delete(self, db: AsyncSession, org_id: uuid.UUID) -> dict:
        await self.org_service.delete_organization(db, org_id)
        return {"success": True, "message": f"Organization {org_id} deleted"}

    # ── Members ───────────────────────────────────────────────

    async def list_members(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> MembershipListResponse:
        members = await self.membership_service.list_members(db, org_id)
        return MembershipListResponse(
            results=[_serialize_membership(m) for m in members],
            total=len(members),
        )

    async def add_member(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        payload: AddMemberRequest,
    ) -> MembershipResponse:
        membership = await self.membership_service.add_member(
            db=db,
            email=payload.email,
            organization_id=org_id,
            role=payload.role,
        )
        return _serialize_membership(membership)

    async def update_member_role(
        self,
        db: AsyncSession,
        member_id: uuid.UUID,
        payload: UpdateMemberRoleRequest,
    ) -> MembershipResponse:
        membership = await self.membership_service.update_role(
            db, member_id, payload.role
        )
        return _serialize_membership(membership)

    async def remove_member(
        self, db: AsyncSession, member_id: uuid.UUID
    ) -> dict:
        await self.membership_service.remove_member(db, member_id)
        return {"success": True, "message": f"Membership {member_id} removed"}

    # ── Invitations ───────────────────────────────────────────

    async def list_invitations(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> InvitationListResponse:
        invitations = await self.invitation_service.list_invitations(db, org_id)
        return InvitationListResponse(
            results=[_serialize_invitation(inv) for inv in invitations],
            total=len(invitations),
        )

    async def create_invitation(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        payload: CreateInvitationRequest,
        user_id: uuid.UUID,
    ) -> InvitationResponse:
        invitation = await self.invitation_service.create_invitation(
            db=db,
            email=payload.email,
            role=payload.role,
            organization_id=org_id,
            invited_by=user_id,
        )
        return _serialize_invitation(invitation)
