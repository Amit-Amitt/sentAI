import uuid
from datetime import UTC, datetime, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.invitation import Invitation


class InvitationRepository:
    """Data access layer for Invitation entities."""

    async def create(
        self,
        db: AsyncSession,
        email: str,
        role: str,
        token: str,
        organization_id: uuid.UUID,
        invited_by: uuid.UUID,
        workspaces: Optional[List[str]] = None,
        expires_in_days: int = 7,
    ) -> Invitation:
        """Creates a new invitation record with optional workspaces scope."""
        db_obj = Invitation(
            email=email,
            role=role,
            token=token,
            organization_id=organization_id,
            invited_by=invited_by,
            status="pending",
            workspaces=workspaces or [],
            expires_at=datetime.now(UTC) + timedelta(days=expires_in_days),
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get_by_token(
        self, db: AsyncSession, token: str
    ) -> Optional[Invitation]:
        """Retrieves an invitation by its unique token."""
        result = await db.execute(
            select(Invitation).where(Invitation.token == token)
        )
        return result.scalars().first()

    async def get_by_id(
        self, db: AsyncSession, invitation_id: uuid.UUID
    ) -> Optional[Invitation]:
        """Retrieves an invitation by primary key."""
        result = await db.execute(
            select(Invitation).where(Invitation.id == invitation_id)
        )
        return result.scalars().first()

    async def list_by_org(
        self, db: AsyncSession, organization_id: uuid.UUID
    ) -> List[Invitation]:
        """Lists all invitations for an organization."""
        result = await db.execute(
            select(Invitation)
            .where(Invitation.organization_id == organization_id)
            .order_by(Invitation.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_status(
        self, db: AsyncSession, invitation: Invitation, status: str
    ) -> Invitation:
        """Updates the status of an invitation."""
        invitation.status = status
        await db.flush()
        return invitation

    async def delete(self, db: AsyncSession, invitation: Invitation) -> bool:
        """Deletes an invitation."""
        await db.delete(invitation)
        await db.flush()
        return True
