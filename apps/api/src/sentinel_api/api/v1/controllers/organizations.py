"""Controller handling mapping logic for organization, member collaboration, and invitation endpoints."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.responses.organization import (
    InvitationListResponse,
    InvitationResponse,
    MemberActivityListResponse,
    MemberActivityResponse,
    MembershipListResponse,
    MembershipResponse,
    OrganizationListResponse,
    OrganizationResponse,
    UserResponse,
    WorkspaceResponse,
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
from sentinel_api.models.activity import MemberActivity
from sentinel_api.models.organization_member import OrganizationMember
from sentinel_api.models.workspace import Workspace
from sentinel_api.models.workspace_member import WorkspaceMember
from sentinel_api.services.activity import ActivityService
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
        workspaces=inv.workspaces or [],
    )


def _serialize_activity(act) -> MemberActivityResponse:
    """Converts an Activity model to response schema."""
    user_resp = None
    if act.user:
        user_resp = UserResponse(
            id=str(act.user.id),
            email=act.user.email,
            full_name=act.user.full_name,
            avatar_url=act.user.avatar_url,
            is_active=act.user.is_active,
        )
    return MemberActivityResponse(
        id=str(act.id),
        organization_id=str(act.organization_id),
        user_id=str(act.user_id) if act.user_id else None,
        action=act.action,
        details=act.details,
        created_at=act.created_at.isoformat() if act.created_at else None,
        user=user_resp,
    )


class OrganizationsController:
    """Controller for organization, membership, activities, and invitation operations."""

    def __init__(
        self,
        org_service: OrganizationService,
        membership_service: MembershipService,
        invitation_service: InvitationService,
        activity_service: ActivityService,
    ) -> None:
        self.org_service = org_service
        self.membership_service = membership_service
        self.invitation_service = invitation_service
        self.activity_service = activity_service

    async def _serialize_membership(
        self, db: AsyncSession, m: OrganizationMember
    ) -> MembershipResponse:
        """Converts an OrganizationMember model to response schema with embedded user and workspaces."""
        # Query workspaces linked to this user in the same organization
        stmt = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(
                WorkspaceMember.user_id == m.user_id,
                Workspace.organization_id == m.organization_id,
            )
        )
        res = await db.execute(stmt)
        workspaces = res.scalars().all()

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
            role=m.role.name if m.role else "viewer",
            user=user_resp,
            created_at=m.created_at.isoformat() if m.created_at else None,
            workspaces=[
                WorkspaceResponse(
                    id=str(ws.id),
                    name=ws.name,
                    slug=ws.slug,
                    environment=ws.environment,
                    description=ws.description,
                    ai_config=ws.ai_config,
                    incident_retention_days=ws.incident_retention_days,
                    organization_id=str(ws.organization_id),
                    created_at=ws.created_at.isoformat() if ws.created_at else None,
                    updated_at=ws.updated_at.isoformat() if ws.updated_at else None,
                )
                for ws in workspaces
            ],
        )

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
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        search: Optional[str] = None,
        role_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> MembershipListResponse:
        members, total = await self.membership_service.list_members(
            db, org_id, search, role_filter, limit, offset
        )
        results = [await self._serialize_membership(db, m) for m in members]
        return MembershipListResponse(results=results, total=total)

    async def add_member(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        payload: AddMemberRequest,
        actor_id: uuid.UUID,
    ) -> MembershipResponse:
        membership = await self.membership_service.add_member(
            db=db,
            email=payload.email,
            organization_id=org_id,
            role=payload.role,
            actor_id=actor_id,
        )
        return await self._serialize_membership(db, membership)

    async def update_member_role(
        self,
        db: AsyncSession,
        member_id: uuid.UUID,
        payload: UpdateMemberRoleRequest,
        actor_id: uuid.UUID,
    ) -> MembershipResponse:
        membership = await self.membership_service.update_role(
            db=db, membership_id=member_id, role=payload.role, actor_id=actor_id
        )
        return await self._serialize_membership(db, membership)

    async def remove_member(
        self, db: AsyncSession, member_id: uuid.UUID, actor_id: uuid.UUID
    ) -> dict:
        await self.membership_service.remove_member(
            db=db, membership_id=member_id, actor_id=actor_id
        )
        return {"success": True, "message": f"Membership {member_id} removed"}

    async def transfer_ownership(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        member_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> MembershipResponse:
        membership = await self.membership_service.transfer_ownership(
            db=db,
            organization_id=org_id,
            target_member_id=member_id,
            actor_id=actor_id,
        )
        return await self._serialize_membership(db, membership)

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
            workspaces=payload.workspaces,
        )
        return _serialize_invitation(invitation)

    async def cancel_invitation(
        self, db: AsyncSession, invitation_id: uuid.UUID, actor_id: uuid.UUID
    ) -> InvitationResponse:
        invitation = await self.invitation_service.cancel_invitation(
            db, invitation_id, actor_id
        )
        return _serialize_invitation(invitation)

    async def resend_invitation(
        self, db: AsyncSession, invitation_id: uuid.UUID, actor_id: uuid.UUID
    ) -> InvitationResponse:
        invitation = await self.invitation_service.resend_invitation(
            db, invitation_id, actor_id
        )
        return _serialize_invitation(invitation)

    # ── Activity ──────────────────────────────────────────────

    async def list_activities(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> MemberActivityListResponse:
        activities = await self.activity_service.list_activities(
            db, org_id, limit, offset
        )
        total = await self.activity_service.count_activities(db, org_id)
        return MemberActivityListResponse(
            results=[_serialize_activity(a) for a in activities],
            total=total,
        )
