import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import List, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.exceptions import EntityNotFoundException, ValidationException
from sentinel_api.models.invitation import Invitation
from sentinel_api.repositories.invitation import InvitationRepository
from sentinel_api.repositories.user import UserRepository
from sentinel_api.repositories.workspace_member import WorkspaceMemberRepository
from sentinel_api.services.activity import ActivityService

logger = structlog.get_logger("sentinel_api.services.invitation")


class InvitationService:
    """Orchestrates invitation lifecycle — create, accept, reject, cancel, resend."""

    def __init__(self) -> None:
        self.repo = InvitationRepository()
        self.user_repo = UserRepository()
        self.ws_member_repo = WorkspaceMemberRepository()
        self.activity_service = ActivityService()

    async def create_invitation(
        self,
        db: AsyncSession,
        email: str,
        role: str,
        organization_id: uuid.UUID,
        invited_by: uuid.UUID,
        workspaces: Optional[List[str]] = None,
    ) -> Invitation:
        """Creates a new invitation with a unique token and workspace scopes."""
        # Check for existing pending invitation
        existing = await self.repo.list_by_org(db, organization_id)
        pending = [
            inv
            for inv in existing
            if inv.email == email and inv.status == "pending"
        ]
        if pending:
            raise ValidationException(
                f"A pending invitation already exists for {email}.",
                error_code="INVITATION_EXISTS",
                status_code=409,
            )

        token = secrets.token_urlsafe(32)
        invitation = await self.repo.create(
            db=db,
            email=email,
            role=role,
            token=token,
            organization_id=organization_id,
            invited_by=invited_by,
            workspaces=workspaces,
        )

        await self.activity_service.log_activity(
            db=db,
            organization_id=organization_id,
            user_id=invited_by,
            action="member_invited",
            details={
                "email": email,
                "role": role,
                "workspaces": workspaces or [],
            },
        )

        logger.info(
            "Invitation created",
            email=email,
            org_id=str(organization_id),
        )
        return invitation

    async def get_by_token(self, db: AsyncSession, token: str) -> Invitation:
        """Retrieves invitation by token."""
        invitation = await self.repo.get_by_token(db, token)
        if not invitation:
            raise EntityNotFoundException(
                "Invitation not found.",
                error_code="INVITATION_NOT_FOUND",
            )
        return invitation

    async def list_invitations(
        self, db: AsyncSession, organization_id: uuid.UUID
    ) -> List[Invitation]:
        """Lists all invitations for an organization."""
        return await self.repo.list_by_org(db, organization_id)

    async def accept_invitation(
        self, db: AsyncSession, token: str, user_id: uuid.UUID
    ) -> Invitation:
        """Accepts an invitation by token and adds user to the organization & workspaces."""
        invitation = await self.repo.get_by_token(db, token)
        if not invitation:
            raise EntityNotFoundException(
                "Invitation not found.",
                error_code="INVITATION_NOT_FOUND",
            )

        if invitation.status != "pending":
            raise ValidationException(
                f"Invitation is already {invitation.status}.",
                error_code="INVITATION_NOT_PENDING",
            )

        expires_at = invitation.expires_at.replace(tzinfo=None) if invitation.expires_at.tzinfo else invitation.expires_at
        now = datetime.now(UTC).replace(tzinfo=None)
        if expires_at < now:
            invitation.status = "expired"
            await db.flush()
            raise ValidationException(
                "Invitation has expired.",
                error_code="INVITATION_EXPIRED",
            )

        user = await self.user_repo.get_by_id(db, user_id)
        if not user:
            raise EntityNotFoundException("User not found.")

        # Accept the invitation
        invitation.status = "accepted"

        # Import MembershipService locally to avoid circular dependency
        from sentinel_api.services.membership import MembershipService
        membership_service = MembershipService()

        # Add to organization members
        await membership_service.add_member(
            db=db,
            email=user.email,
            organization_id=invitation.organization_id,
            role=invitation.role,
            actor_id=user_id,
        )

        # Add to scoped workspaces
        for ws_id_str in invitation.workspaces:
            try:
                ws_id = uuid.UUID(ws_id_str)
                await self.ws_member_repo.create(db, user_id=user_id, workspace_id=ws_id)
            except Exception:
                logger.warning("Failed to add user to workspace from invitation scope", workspace_id=ws_id_str)

        await self.activity_service.log_activity(
            db=db,
            organization_id=invitation.organization_id,
            user_id=user_id,
            action="invitation_accepted",
            details={
                "email": user.email,
                "role": invitation.role,
            },
        )

        await db.flush()
        logger.info("Invitation accepted", token=token[:8] + "...", user_id=str(user_id))
        return invitation

    async def reject_invitation(
        self, db: AsyncSession, token: str, user_id: uuid.UUID
    ) -> Invitation:
        """Rejects an invitation."""
        invitation = await self.repo.get_by_token(db, token)
        if not invitation:
            raise EntityNotFoundException(
                "Invitation not found.",
                error_code="INVITATION_NOT_FOUND",
            )

        if invitation.status != "pending":
            raise ValidationException(
                f"Invitation is already {invitation.status}.",
                error_code="INVITATION_NOT_PENDING",
            )

        invitation.status = "rejected"

        await self.activity_service.log_activity(
            db=db,
            organization_id=invitation.organization_id,
            user_id=user_id,
            action="invitation_rejected",
            details={"email": invitation.email},
        )

        await db.flush()
        logger.info("Invitation rejected", token=token[:8] + "...")
        return invitation

    async def cancel_invitation(
        self, db: AsyncSession, invitation_id: uuid.UUID, actor_id: uuid.UUID
    ) -> Invitation:
        """Cancels a pending invitation."""
        invitation = await self.repo.get_by_id(db, invitation_id)
        if not invitation:
            raise EntityNotFoundException(
                "Invitation not found.",
                error_code="INVITATION_NOT_FOUND",
            )

        if invitation.status != "pending":
            raise ValidationException(
                f"Cannot cancel an invitation that is {invitation.status}.",
                error_code="INVITATION_NOT_PENDING",
            )

        invitation.status = "cancelled"

        await self.activity_service.log_activity(
            db=db,
            organization_id=invitation.organization_id,
            user_id=actor_id,
            action="invitation_cancelled",
            details={"email": invitation.email},
        )

        await db.flush()
        logger.info("Invitation cancelled", invitation_id=str(invitation_id))
        return invitation

    async def resend_invitation(
        self, db: AsyncSession, invitation_id: uuid.UUID, actor_id: uuid.UUID
    ) -> Invitation:
        """Resends a pending invitation by extending its expiration."""
        invitation = await self.repo.get_by_id(db, invitation_id)
        if not invitation:
            raise EntityNotFoundException(
                "Invitation not found.",
                error_code="INVITATION_NOT_FOUND",
            )

        # Extend expiry by another 7 days
        invitation.expires_at = datetime.now(UTC) + timedelta(days=7)
        invitation.status = "pending"  # if expired previously

        await self.activity_service.log_activity(
            db=db,
            organization_id=invitation.organization_id,
            user_id=actor_id,
            action="invitation_resent",
            details={"email": invitation.email},
        )

        await db.flush()
        logger.info("Invitation resent", invitation_id=str(invitation_id))
        return invitation
