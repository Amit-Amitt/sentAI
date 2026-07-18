"""API routes for the Integrations Marketplace."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, Request

from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.controllers.integration import IntegrationController
from sentinel_api.api.v1.dependencies.current_user import get_current_user
from sentinel_api.database.session import get_db_session
from sentinel_api.models.user import User
from sentinel_api.schemas.integration import (
    IntegrationProviderResponse,
    WorkspaceIntegrationResponse,
    WorkspaceIntegrationCreate,
    WorkspaceIntegrationUpdate,
    ConnectionTestResponse,
    SyncTriggerResponse,
    IntegrationHistoryResponse,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


def get_controller() -> IntegrationController:
    """Dependency helper returning IntegrationController instance."""
    return IntegrationController()


@router.get("", response_model=List[IntegrationProviderResponse])
async def list_integrations(
    workspace_id: Optional[uuid.UUID] = Query(None, description="Workspace ID scoping connections"),
    db: AsyncSession = Depends(get_db_session),
    controller: IntegrationController = Depends(get_controller),
) -> List[Any]:
    """Lists all available integration providers, with connection status if workspace_id is provided."""
    return await controller.list_providers(db=db, workspace_id=workspace_id)


@router.get("/{id}", response_model=IntegrationProviderResponse)
async def get_integration(
    id: uuid.UUID,
    workspace_id: Optional[uuid.UUID] = Query(None, description="Workspace ID scoping the connection details"),
    db: AsyncSession = Depends(get_db_session),
    controller: IntegrationController = Depends(get_controller),
) -> Any:
    """Fetches details of a single integration provider and active workspace connection if configured."""
    return await controller.get_provider(db=db, provider_id=id, workspace_id=workspace_id)


@router.post("", response_model=WorkspaceIntegrationResponse, status_code=201)
async def connect_integration(
    request: Request,
    payload: WorkspaceIntegrationCreate,
    workspace_id: uuid.UUID = Query(..., description="Workspace ID mapping the connection"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: IntegrationController = Depends(get_controller),
) -> Any:
    """Connects/configures an integration for a workspace."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await controller.connect(
        db=db,
        workspace_id=workspace_id,
        payload=payload,
        current_user_id=user.id,
        client_host=ip_address,
        user_agent=user_agent,
    )


@router.patch("/{id}", response_model=WorkspaceIntegrationResponse)
async def update_integration(
    id: uuid.UUID,
    payload: WorkspaceIntegrationUpdate,
    request: Request,
    workspace_id: uuid.UUID = Query(..., description="Workspace ID mapping the connection"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: IntegrationController = Depends(get_controller),
) -> Any:
    """Modifies configurations or toggle status flags for an active integration."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await controller.update(
        db=db,
        connection_id=id,
        workspace_id=workspace_id,
        payload=payload,
        current_user_id=user.id,
        client_host=ip_address,
        user_agent=user_agent,
    )


@router.delete("/{id}", response_model=Dict[str, bool])
async def delete_integration(
    id: uuid.UUID,
    request: Request,
    workspace_id: uuid.UUID = Query(..., description="Workspace ID mapping the connection"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: IntegrationController = Depends(get_controller),
) -> Dict[str, bool]:
    """Permanently deletes an active integration connection from the database."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    success = await controller.delete(
        db=db,
        connection_id=id,
        workspace_id=workspace_id,
        current_user_id=user.id,
        client_host=ip_address,
        user_agent=user_agent,
    )
    return {"success": success}


@router.post("/{id}/connect", response_model=WorkspaceIntegrationResponse)
async def connect_existing_integration(
    id: uuid.UUID,
    request: Request,
    payload: WorkspaceIntegrationCreate,
    workspace_id: uuid.UUID = Query(..., description="Workspace ID mapping the connection"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: IntegrationController = Depends(get_controller),
) -> Any:
    """Establishes or restores an active connection status for a provider."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Connect payload sets the provider_id
    payload.provider_id = id

    return await controller.connect(
        db=db,
        workspace_id=workspace_id,
        payload=payload,
        current_user_id=user.id,
        client_host=ip_address,
        user_agent=user_agent,
    )


@router.post("/{id}/disconnect", response_model=WorkspaceIntegrationResponse)
async def disconnect_integration(
    id: uuid.UUID,
    request: Request,
    workspace_id: uuid.UUID = Query(..., description="Workspace ID mapping the connection"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: IntegrationController = Depends(get_controller),
) -> Any:
    """Deactivates and disconnects an integration."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await controller.disconnect(
        db=db,
        connection_id=id,
        workspace_id=workspace_id,
        current_user_id=user.id,
        client_host=ip_address,
        user_agent=user_agent,
    )


@router.post("/{id}/test", response_model=ConnectionTestResponse)
async def test_integration(
    id: uuid.UUID,
    workspace_id: uuid.UUID = Query(..., description="Workspace ID mapping the connection"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: IntegrationController = Depends(get_controller),
) -> Any:
    """Performs simulated health and ping verification against a remote system."""
    return await controller.test(db=db, connection_id=id, workspace_id=workspace_id)


@router.post("/{id}/sync", response_model=SyncTriggerResponse)
async def sync_integration(
    id: uuid.UUID,
    workspace_id: uuid.UUID = Query(..., description="Workspace ID mapping the connection"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: IntegrationController = Depends(get_controller),
) -> Any:
    """Launches an immediate data synchronization process for the integration."""
    return await controller.sync(db=db, connection_id=id, workspace_id=workspace_id)


@router.get("/{id}/history", response_model=IntegrationHistoryResponse)
async def get_integration_history(
    id: uuid.UUID,
    workspace_id: uuid.UUID = Query(..., description="Workspace ID scoping the logs"),
    db: AsyncSession = Depends(get_db_session),
    controller: IntegrationController = Depends(get_controller),
) -> Any:
    """Retrieves sync logs and configuration update audit history details."""
    return await controller.get_history(db=db, connection_id=id, workspace_id=workspace_id)
