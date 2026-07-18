import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.workspace_member import WorkspaceMember


class WorkspaceMemberRepository:
    """Repository managing user associations with workspaces."""

    async def create(
        self, db: AsyncSession, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> WorkspaceMember:
        """Adds a user to a workspace."""
        member = WorkspaceMember(user_id=user_id, workspace_id=workspace_id)
        db.add(member)
        await db.flush()
        return member

    async def get(
        self, db: AsyncSession, user_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> WorkspaceMember | None:
        """Fetches a workspace membership if it exists."""
        stmt = select(WorkspaceMember).where(
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.workspace_id == workspace_id,
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_workspace(
        self, db: AsyncSession, workspace_id: uuid.UUID
    ) -> Sequence[WorkspaceMember]:
        """Lists all members of a workspace."""
        stmt = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id
        )
        res = await db.execute(stmt)
        return res.scalars().all()

    async def list_by_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> Sequence[WorkspaceMember]:
        """Lists all workspace memberships for a user."""
        stmt = select(WorkspaceMember).where(WorkspaceMember.user_id == user_id)
        res = await db.execute(stmt)
        return res.scalars().all()

    async def delete(self, db: AsyncSession, member: WorkspaceMember) -> None:
        """Removes a user from a workspace."""
        await db.delete(member)
        await db.flush()
