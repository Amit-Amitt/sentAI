import uuid
from typing import Any, Dict, List, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.activity import MemberActivity


class ActivityRepository:
    """Repository managing audit logging of team activities."""

    async def create(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        action: str,
        details: Dict[str, Any],
    ) -> MemberActivity:
        """Logs a new collaboration/team management activity."""
        activity = MemberActivity(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            details=details,
        )
        db.add(activity)
        await db.flush()
        return activity

    async def list_by_org(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[MemberActivity]:
        """Lists team activities for an organization, descending order."""
        stmt = (
            select(MemberActivity)
            .where(MemberActivity.organization_id == organization_id)
            .order_by(MemberActivity.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await db.execute(stmt)
        return res.scalars().all()

    async def count_by_org(
        self, db: AsyncSession, organization_id: uuid.UUID
    ) -> int:
        """Returns total count of activities for an organization."""
        stmt = (
            select(func.count())
            .select_from(MemberActivity)
            .where(MemberActivity.organization_id == organization_id)
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none() or 0
