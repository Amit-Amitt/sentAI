"""API routes for workspace endpoints."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.controllers.workspaces import WorkspacesController
from sentinel_api.api.v1.dependencies.services import get_workspace_service
from sentinel_api.api.v1.responses.organization import (
    WorkspaceListResponse,
    WorkspaceResponse,
)
from sentinel_api.api.v1.responses.schemas import DeleteResponse
from sentinel_api.api.v1.validators.workspace import (
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
)
from sentinel_api.database.session import get_db_session
from sentinel_api.services.workspace import WorkspaceService

router = APIRouter(tags=["workspaces"])


def get_controller(
    service: WorkspaceService = Depends(get_workspace_service),
) -> WorkspacesController:
    return WorkspacesController(service)


# ── Scoped under organization ─────────────────────────────────


@router.post(
    "/organizations/{org_id}/workspaces",
    response_model=WorkspaceResponse,
    status_code=201,
)
async def create_workspace(
    org_id: uuid.UUID,
    payload: CreateWorkspaceRequest,
    db: AsyncSession = Depends(get_db_session),
    controller: WorkspacesController = Depends(get_controller),
) -> WorkspaceResponse:
    """Creates a new workspace within an organization."""
    return await controller.create(db, org_id, payload)


@router.get(
    "/organizations/{org_id}/workspaces",
    response_model=WorkspaceListResponse,
)
async def list_workspaces(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: WorkspacesController = Depends(get_controller),
) -> WorkspaceListResponse:
    """Lists all workspaces within an organization."""
    return await controller.list_all(db, org_id)


# ── Direct workspace access ───────────────────────────────────


@router.get("/workspaces/{ws_id}", response_model=WorkspaceResponse)
async def get_workspace(
    ws_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: WorkspacesController = Depends(get_controller),
) -> WorkspaceResponse:
    """Returns details of a specific workspace."""
    return await controller.get(db, ws_id)


@router.patch("/workspaces/{ws_id}", response_model=WorkspaceResponse)
async def update_workspace(
    ws_id: uuid.UUID,
    payload: UpdateWorkspaceRequest,
    db: AsyncSession = Depends(get_db_session),
    controller: WorkspacesController = Depends(get_controller),
) -> WorkspaceResponse:
    """Updates workspace settings."""
    return await controller.update(db, ws_id, payload)


@router.delete("/workspaces/{ws_id}", response_model=DeleteResponse)
async def delete_workspace(
    ws_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: WorkspacesController = Depends(get_controller),
) -> DeleteResponse:
    """Deletes a workspace."""
    res = await controller.delete(db, ws_id)
    return DeleteResponse(success=res["success"], message=res["message"])
