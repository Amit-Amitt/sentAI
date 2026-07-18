"""API routes for API Key management endpoints."""

import uuid
from fastapi import APIRouter, Depends, Query, Request

from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.controllers.api_keys import ApiKeysController
from sentinel_api.api.v1.dependencies.current_user import get_current_user
from sentinel_api.api.v1.dependencies.services import get_api_key_service
from sentinel_api.api.v1.responses.schemas import DeleteResponse
from sentinel_api.database.session import get_db_session
from sentinel_api.models.user import User
from sentinel_api.schemas.api_key import (
    ApiKeyAuditListResponse,
    ApiKeyListResponse,
    ApiKeyResponse,
    ApiKeyUpdate,
    ApiKeyUsageStatsResponse,
    ApiKeyWithSecretResponse,
    ApiKeyCreate,
)
from sentinel_api.services.api_key import ApiKeyService

router = APIRouter(prefix="/apikeys", tags=["apikeys"])


def get_controller(
    service: ApiKeyService = Depends(get_api_key_service),
) -> ApiKeysController:
    """Dependency injection helper retrieving ApiKeysController."""
    return ApiKeysController(service)


@router.post("", response_model=ApiKeyWithSecretResponse, status_code=201)
async def create_api_key(
    request: Request,
    payload: ApiKeyCreate,
    workspace_id: uuid.UUID = Query(..., description="Workspace owning the API Key"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: ApiKeysController = Depends(get_controller),
) -> ApiKeyWithSecretResponse:
    """Creates a new secure API Key for the selected workspace."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await controller.create(
        db=db,
        workspace_id=workspace_id,
        payload=payload,
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.get("", response_model=ApiKeyListResponse)
async def list_api_keys(
    workspace_id: uuid.UUID = Query(..., description="Workspace ID scoping the keys"),
    db: AsyncSession = Depends(get_db_session),
    controller: ApiKeysController = Depends(get_controller),
) -> ApiKeyListResponse:
    """Returns a list of all active or historical API keys for a workspace."""
    return await controller.list_workspace_keys(db=db, workspace_id=workspace_id)


@router.get("/{id}", response_model=ApiKeyResponse)
async def get_api_key(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: ApiKeysController = Depends(get_controller),
) -> ApiKeyResponse:
    """Returns the metadata for a single API key."""
    return await controller.get(db=db, api_key_id=id)


@router.patch("/{id}", response_model=ApiKeyResponse)
async def update_api_key(
    id: uuid.UUID,
    payload: ApiKeyUpdate,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: ApiKeysController = Depends(get_controller),
) -> ApiKeyResponse:
    """Modifies the metadata or scope configurations of an existing key."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await controller.update(
        db=db,
        api_key_id=id,
        payload=payload,
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.post("/{id}/rotate", response_model=ApiKeyWithSecretResponse)
async def rotate_api_key(
    id: uuid.UUID,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: ApiKeysController = Depends(get_controller),
) -> ApiKeyWithSecretResponse:
    """Rotates the secret key. The old secret is immediately invalidated."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await controller.rotate(
        db=db,
        api_key_id=id,
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.post("/{id}/revoke", response_model=ApiKeyResponse)
async def revoke_api_key(
    id: uuid.UUID,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: ApiKeysController = Depends(get_controller),
) -> ApiKeyResponse:
    """Permanently revokes and invalidates the key."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await controller.revoke(
        db=db,
        api_key_id=id,
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.delete("/{id}", response_model=DeleteResponse)
async def delete_api_key(
    id: uuid.UUID,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: ApiKeysController = Depends(get_controller),
) -> DeleteResponse:
    """Deletes an API key record."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await controller.delete(
        db=db,
        api_key_id=id,
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.post("/{id}/copy", response_model=DeleteResponse)
async def copy_api_key(
    id: uuid.UUID,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    controller: ApiKeysController = Depends(get_controller),
) -> DeleteResponse:
    """Records a key copy action for audit history."""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    return await controller.copy(
        db=db,
        api_key_id=id,
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )


@router.get("/{id}/usage", response_model=ApiKeyUsageStatsResponse)
async def get_api_key_usage(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: ApiKeysController = Depends(get_controller),
) -> ApiKeyUsageStatsResponse:
    """Fetches key activity log records, audits, and aggregated transaction count metrics."""
    return await controller.get_usage(db=db, api_key_id=id)


@router.get("/{id}/audits", response_model=ApiKeyAuditListResponse)
async def get_api_key_audits(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: ApiKeysController = Depends(get_controller),
) -> ApiKeyAuditListResponse:
    """Fetches audit history for a single API key."""
    return await controller.list_audits(db=db, api_key_id=id)
