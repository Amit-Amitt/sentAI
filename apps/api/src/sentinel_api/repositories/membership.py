"""Repository for Membership entity database operations."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.membership import Membership


class MembershipRepository:
    """Data access layer for Membership entities."""

    async def create(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        role: str = "engineer",
        workspace_id: Optional[uuid.UUID] = None,
    ) -> Membership:
        """Creates a new membership record."""
        db_obj = Membership(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
            workspace_id=workspace_id,
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get(
        self, db: AsyncSession, membership_id: uuid.UUID
    ) -> Optional[Membership]:
        """Retrieves a membership by primary key."""
        result = await db.execute(
            select(Membership).where(Membership.id == membership_id)
        )
        return result.scalars().first()

    async def get_by_user_and_org(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[Membership]:
        """Retrieves the org-level membership for a specific user and org."""
        result = await db.execute(
            select(Membership)
            .where(Membership.user_id == user_id)
            .where(Membership.organization_id == organization_id)
            .where(Membership.workspace_id.is_(None))
        )
        return result.scalars().first()

    async def list_by_org(
        self, db: AsyncSession, organization_id: uuid.UUID
    ) -> List[Membership]:
        """Lists all org-level memberships for an organization."""
        result = await db.execute(
            select(Membership)
            .where(Membership.organization_id == organization_id)
            .where(Membership.workspace_id.is_(None))
            .order_by(Membership.created_at)
        )
        return list(result.scalars().all())

    async def list_by_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> List[Membership]:
        """Lists all org-level memberships for a user."""
        result = await db.execute(
            select(Membership)
            .where(Membership.user_id == user_id)
            .where(Membership.workspace_id.is_(None))
            .order_by(Membership.created_at)
        )
        return list(result.scalars().all())

    async def update_role(
        self, db: AsyncSession, membership: Membership, role: str
    ) -> Membership:
        """Updates the role on a membership."""
        membership.role = role
        await db.flush()
        return membership

    async def delete(self, db: AsyncSession, membership: Membership) -> bool:
        """Deletes a membership."""
        await db.delete(membership)
        await db.flush()
        return True
