"""Repository for Organization entity database operations."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.membership import Membership
from sentinel_api.models.organization import Organization


class OrganizationRepository:
    """Data access layer for Organization entities."""

    async def create(
        self,
        db: AsyncSession,
        name: str,
        slug: str,
        owner_id: uuid.UUID,
        industry: Optional[str] = None,
        region: Optional[str] = None,
        timezone: str = "UTC",
    ) -> Organization:
        """Creates a new organization record."""
        db_obj = Organization(
            name=name,
            slug=slug,
            owner_id=owner_id,
            industry=industry,
            region=region,
            timezone=timezone,
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get_by_id(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> Optional[Organization]:
        """Retrieves an organization by primary key."""
        result = await db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalars().first()

    async def get_by_slug(
        self, db: AsyncSession, slug: str
    ) -> Optional[Organization]:
        """Retrieves an organization by unique slug."""
        result = await db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        return result.scalars().first()

    async def list_by_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> List[Organization]:
        """Lists all organizations a user is a member of."""
        stmt = (
            select(Organization)
            .join(Membership, Membership.organization_id == Organization.id)
            .where(Membership.user_id == user_id)
            .where(Membership.workspace_id.is_(None))
            .distinct()
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        org: Organization,
        **kwargs: object,
    ) -> Organization:
        """Updates organization fields."""
        for key, value in kwargs.items():
            if hasattr(org, key) and value is not None:
                setattr(org, key, value)
        await db.flush()
        return org

    async def delete(self, db: AsyncSession, org: Organization) -> bool:
        """Deletes an organization and cascades to children."""
        await db.delete(org)
        await db.flush()
        return True
