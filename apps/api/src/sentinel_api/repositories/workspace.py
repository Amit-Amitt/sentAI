"""Repository for Workspace entity database operations."""

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.workspace import Workspace


class WorkspaceRepository:
    """Data access layer for Workspace entities."""

    async def create(
        self,
        db: AsyncSession,
        name: str,
        slug: str,
        organization_id: uuid.UUID,
        environment: str = "development",
        description: Optional[str] = None,
        ai_config: Optional[Dict[str, Any]] = None,
        incident_retention_days: int = 90,
    ) -> Workspace:
        """Creates a new workspace record."""
        db_obj = Workspace(
            name=name,
            slug=slug,
            organization_id=organization_id,
            environment=environment,
            description=description,
            ai_config=ai_config or {},
            incident_retention_days=incident_retention_days,
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get_by_id(
        self, db: AsyncSession, ws_id: uuid.UUID
    ) -> Optional[Workspace]:
        """Retrieves a workspace by primary key."""
        result = await db.execute(select(Workspace).where(Workspace.id == ws_id))
        return result.scalars().first()

    async def list_by_organization(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> List[Workspace]:
        """Lists all workspaces within an organization."""
        result = await db.execute(
            select(Workspace)
            .where(Workspace.organization_id == org_id)
            .order_by(Workspace.created_at)
        )
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        ws: Workspace,
        **kwargs: object,
    ) -> Workspace:
        """Updates workspace fields."""
        for key, value in kwargs.items():
            if hasattr(ws, key) and value is not None:
                setattr(ws, key, value)
        await db.flush()
        return ws

    async def delete(self, db: AsyncSession, ws: Workspace) -> bool:
        """Deletes a workspace."""
        await db.delete(ws)
        await db.flush()
        return True
