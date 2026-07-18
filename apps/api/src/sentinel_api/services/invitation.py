"""Service layer for Invitation business logic."""

import secrets
import uuid
from typing import List

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.exceptions import EntityNotFoundException, ValidationException
from sentinel_api.models.invitation import Invitation
from sentinel_api.repositories.invitation import InvitationRepository

logger = structlog.get_logger("sentinel_api.services.invitation")


class InvitationService:
    """Orchestrates invitation lifecycle — create, accept, revoke, list."""

    def __init__(self) -> None:
        self.repo = InvitationRepository()

    async def create_invitation(
        self,
        db: AsyncSession,
        email: str,
        role: str,
        organization_id: uuid.UUID,
        invited_by: uuid.UUID,
    ) -> Invitation:
        """Creates a new invitation with a unique token."""
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
        )
        logger.info(
            "Invitation created",
            email=email,
            org_id=str(organization_id),
        )
        return invitation

    async def list_invitations(
        self, db: AsyncSession, organization_id: uuid.UUID
    ) -> List[Invitation]:
        """Lists all invitations for an organization."""
        return await self.repo.list_by_org(db, organization_id)

    async def accept_invitation(
        self, db: AsyncSession, token: str
    ) -> Invitation:
        """Accepts an invitation by token."""
        invitation = await self.repo.get_by_token(db, token)
        if not invitation:
            raise EntityNotFoundException(
                "Invitation not found or expired.",
                error_code="INVITATION_NOT_FOUND",
            )
        if invitation.status != "pending":
            raise ValidationException(
                f"Invitation is already {invitation.status}.",
                error_code="INVITATION_NOT_PENDING",
            )

        invitation = await self.repo.update_status(db, invitation, "accepted")
        logger.info("Invitation accepted", token=token[:8] + "...")
        return invitation

    async def revoke_invitation(
        self, db: AsyncSession, invitation_id: uuid.UUID
    ) -> Invitation:
        """Revokes a pending invitation."""
        invitation = await self.repo.get_by_id(db, invitation_id)
        if not invitation:
            raise EntityNotFoundException(
                "Invitation not found.",
                error_code="INVITATION_NOT_FOUND",
            )
        if invitation.status != "pending":
            raise ValidationException(
                f"Cannot revoke an invitation that is {invitation.status}.",
                error_code="INVITATION_NOT_PENDING",
            )

        invitation = await self.repo.update_status(db, invitation, "revoked")
        logger.info("Invitation revoked", invitation_id=str(invitation_id))
        return invitation
