import uuid
from typing import Any, Dict, List, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.activity import MemberActivity
from sentinel_api.repositories.activity import ActivityRepository


class ActivityService:
    """Service layer coordinating team management audit trails."""

    def __init__(self) -> None:
        self.activity_repo = ActivityRepository()

    async def log_activity(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        action: str,
        details: Dict[str, Any],
    ) -> MemberActivity:
        """Helper to create audit trails for team actions."""
        return await self.activity_repo.create(
            db, organization_id, user_id, action, details
        )

    async def list_activities(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[MemberActivity]:
        """Fetch audit log history."""
        return await self.activity_repo.list_by_org(
            db, organization_id, limit, offset
        )

    async def count_activities(
        self, db: AsyncSession, organization_id: uuid.UUID
    ) -> int:
        """Returns total activity count."""
        return await self.activity_repo.count_by_org(db, organization_id)
