import uuid
from typing import List, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.organization_member import OrganizationMember
from sentinel_api.models.role import Role
from sentinel_api.models.user import User


class MembershipRepository:
    """Data access layer for OrganizationMember entities (formerly Membership)."""

    async def get_role_by_name(self, db: AsyncSession, name: str) -> Role | None:
        """Retrieves a Role model by its string name."""
        stmt = select(Role).where(Role.name == name.lower())
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        role: str = "engineer",
        status: str = "active",
    ) -> OrganizationMember:
        """Creates a new OrganizationMember record, resolving role name to ID."""
        role_obj = await self.get_role_by_name(db, role)
        if not role_obj:
            raise ValueError(f"Role '{role}' not found in database.")

        db_obj = OrganizationMember(
            user_id=user_id,
            organization_id=organization_id,
            role_id=role_obj.id,
            status=status,
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get(
        self, db: AsyncSession, membership_id: uuid.UUID
    ) -> Optional[OrganizationMember]:
        """Retrieves an organization member by primary key."""
        result = await db.execute(
            select(OrganizationMember).where(OrganizationMember.id == membership_id)
        )
        return result.scalars().first()

    async def get_by_user_and_org(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[OrganizationMember]:
        """Retrieves membership for a specific user and org."""
        result = await db.execute(
            select(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
            .where(OrganizationMember.organization_id == organization_id)
        )
        return result.scalars().first()

    async def list_by_org(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        search: Optional[str] = None,
        role_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[OrganizationMember]:
        """Lists members with search, role filtering, and pagination support."""
        stmt = select(OrganizationMember).join(User).where(
            OrganizationMember.organization_id == organization_id
        )

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                (User.full_name.ilike(search_pattern))
                | (User.email.ilike(search_pattern))
            )

        if role_filter:
            stmt = stmt.join(Role).where(Role.name == role_filter.lower())

        stmt = stmt.order_by(OrganizationMember.created_at).offset(offset).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        search: Optional[str] = None,
        role_filter: Optional[str] = None,
    ) -> int:
        """Returns total member count matching search/filter parameters."""
        stmt = (
            select(func.count())
            .select_from(OrganizationMember)
            .join(User)
            .where(OrganizationMember.organization_id == organization_id)
        )

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                (User.full_name.ilike(search_pattern))
                | (User.email.ilike(search_pattern))
            )

        if role_filter:
            stmt = stmt.join(Role).where(Role.name == role_filter.lower())

        result = await db.execute(stmt)
        return result.scalar_one_or_none() or 0

    async def list_by_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> List[OrganizationMember]:
        """Lists all organization memberships for a user."""
        result = await db.execute(
            select(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
            .order_by(OrganizationMember.created_at)
        )
        return list(result.scalars().all())

    async def update_role(
        self, db: AsyncSession, membership: OrganizationMember, role: str
    ) -> OrganizationMember:
        """Updates the member role by resolving role string to model ID."""
        role_obj = await self.get_role_by_name(db, role)
        if not role_obj:
            raise ValueError(f"Role '{role}' not found in database.")

        membership.role_id = role_obj.id
        membership.role = role_obj
        await db.flush()
        return membership

    async def delete(
        self, db: AsyncSession, membership: OrganizationMember
    ) -> bool:
        """Deletes an organization member record."""
        await db.delete(membership)
        await db.flush()
        return True
