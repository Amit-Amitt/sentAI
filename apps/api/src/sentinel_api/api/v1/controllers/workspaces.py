"""Controller handling mapping logic for workspace endpoints."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.responses.organization import (
    WorkspaceListResponse,
    WorkspaceResponse,
)
from sentinel_api.api.v1.validators.workspace import (
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
)
from sentinel_api.services.workspace import WorkspaceService


def _serialize_workspace(ws) -> WorkspaceResponse:
    """Converts a Workspace model to response schema."""
    return WorkspaceResponse(
        id=str(ws.id),
        name=ws.name,
        slug=ws.slug,
        environment=ws.environment,
        description=ws.description,
        ai_config=ws.ai_config or {},
        incident_retention_days=ws.incident_retention_days,
        organization_id=str(ws.organization_id),
        created_at=ws.created_at.isoformat() if ws.created_at else None,
        updated_at=ws.updated_at.isoformat() if ws.updated_at else None,
    )


class WorkspacesController:
    """Controller for workspace operations."""

    def __init__(self, service: WorkspaceService) -> None:
        self.service = service

    async def create(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        payload: CreateWorkspaceRequest,
    ) -> WorkspaceResponse:
        ws = await self.service.create_workspace(
            db=db,
            name=payload.name,
            slug=payload.slug,
            organization_id=org_id,
            environment=payload.environment,
            description=payload.description,
        )
        return _serialize_workspace(ws)

    async def get(
        self, db: AsyncSession, ws_id: uuid.UUID
    ) -> WorkspaceResponse:
        ws = await self.service.get_workspace(db, ws_id)
        return _serialize_workspace(ws)

    async def list_all(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> WorkspaceListResponse:
        workspaces = await self.service.list_workspaces(db, org_id)
        return WorkspaceListResponse(
            results=[_serialize_workspace(ws) for ws in workspaces],
            total=len(workspaces),
        )

    async def update(
        self,
        db: AsyncSession,
        ws_id: uuid.UUID,
        payload: UpdateWorkspaceRequest,
    ) -> WorkspaceResponse:
        update_data = payload.model_dump(exclude_none=True)
        ws = await self.service.update_workspace(db, ws_id, **update_data)
        return _serialize_workspace(ws)

    async def delete(self, db: AsyncSession, ws_id: uuid.UUID) -> dict:
        await self.service.delete_workspace(db, ws_id)
        return {"success": True, "message": f"Workspace {ws_id} deleted"}
