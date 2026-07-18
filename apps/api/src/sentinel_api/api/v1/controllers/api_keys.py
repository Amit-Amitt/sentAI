"""Controller handling mapping and serialization logic for API Key endpoints."""

import uuid
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.responses.schemas import DeleteResponse
from sentinel_api.schemas.api_key import (
    ApiKeyAuditResponse,
    ApiKeyAuditListResponse,
    ApiKeyListResponse,
    ApiKeyResponse,
    ApiKeyUsageResponse,
    ApiKeyUsageStatsResponse,
    ApiKeyWithSecretResponse,
    ApiKeyCreate,
    ApiKeyUpdate,
)
from sentinel_api.services.api_key import ApiKeyService


def _serialize_api_key(key) -> ApiKeyResponse:
    """Converts an ApiKey model to its response schema representation."""
    return ApiKeyResponse(
        id=str(key.id),
        name=key.name,
        description=key.description,
        prefix=key.prefix,
        environment=key.environment,
        scopes=[p.scope for p in key.permissions],
        created_by_id=str(key.created_by_id) if key.created_by_id else None,
        created_at=key.created_at.isoformat() if key.created_at else None,
        last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
        expires_at=key.expires_at.isoformat() if key.expires_at else None,
        status=key.status,
        workspace_id=str(key.workspace_id),
    )


def _serialize_api_key_with_secret(key, secret: str) -> ApiKeyWithSecretResponse:
    """Converts ApiKey model and raw secret string to the reveal-once response schema."""
    return ApiKeyWithSecretResponse(
        id=str(key.id),
        name=key.name,
        description=key.description,
        prefix=key.prefix,
        environment=key.environment,
        scopes=[p.scope for p in key.permissions],
        created_by_id=str(key.created_by_id) if key.created_by_id else None,
        created_at=key.created_at.isoformat() if key.created_at else None,
        last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
        expires_at=key.expires_at.isoformat() if key.expires_at else None,
        status=key.status,
        workspace_id=str(key.workspace_id),
        secret=secret,
    )


def _serialize_usage(usage) -> ApiKeyUsageResponse:
    """Converts ApiKeyUsage to response schema."""
    return ApiKeyUsageResponse(
        id=str(usage.id),
        endpoint=usage.endpoint,
        method=usage.method,
        status_code=usage.status_code,
        response_time_ms=usage.response_time_ms,
        ip_address=usage.ip_address,
        user_agent=usage.user_agent,
        timestamp=usage.timestamp.isoformat() if usage.timestamp else None,
    )


def _serialize_audit(audit) -> ApiKeyAuditResponse:
    """Converts ApiKeyAudit to response schema."""
    return ApiKeyAuditResponse(
        id=str(audit.id),
        action=audit.action,
        performed_by_id=str(audit.performed_by_id) if audit.performed_by_id else None,
        performed_by_name=audit.performed_by.full_name if audit.performed_by else None,
        ip_address=audit.ip_address,
        user_agent=audit.user_agent,
        details=audit.details or {},
        timestamp=audit.timestamp.isoformat() if audit.timestamp else None,
    )


class ApiKeysController:
    """Controller orchestrating API Key HTTP input validation and outputs."""

    def __init__(self, service: ApiKeyService) -> None:
        self.service = service

    async def create(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        payload: ApiKeyCreate,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ApiKeyWithSecretResponse:
        """Executes API Key creation logic and returns the full credentials."""
        key, secret = await self.service.create_key(
            db=db,
            workspace_id=workspace_id,
            name=payload.name,
            environment=payload.environment,
            scopes=payload.scopes,
            created_by_id=user_id,
            description=payload.description,
            expires_at=payload.expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return _serialize_api_key_with_secret(key, secret)

    async def list_workspace_keys(
        self, db: AsyncSession, workspace_id: uuid.UUID
    ) -> ApiKeyListResponse:
        """Lists all keys in a workspace."""
        keys = await self.service.list_keys(db, workspace_id)
        return ApiKeyListResponse(
            results=[_serialize_api_key(k) for k in keys],
            total=len(keys),
        )

    async def get(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
    ) -> ApiKeyResponse:
        """Fetches a single API Key."""
        key = await self.service.get_key(db=db, api_key_id=api_key_id)
        return _serialize_api_key(key)

    async def update(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        payload: ApiKeyUpdate,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ApiKeyResponse:
        """Updates metadata properties of an API Key."""
        update_data = payload.model_dump(exclude_none=True)
        scopes = update_data.pop("scopes", None)

        key = await self.service.update_key(
            db=db,
            api_key_id=api_key_id,
            performed_by_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            scopes=scopes,
            **update_data,
        )
        return _serialize_api_key(key)

    async def rotate(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ApiKeyWithSecretResponse:
        """Generates a new key credential for an existing API Key record."""
        key, secret = await self.service.rotate_key(
            db=db,
            api_key_id=api_key_id,
            performed_by_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return _serialize_api_key_with_secret(key, secret)

    async def revoke(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ApiKeyResponse:
        """Permanently disables and revokes an API Key."""
        key = await self.service.revoke_key(
            db=db,
            api_key_id=api_key_id,
            performed_by_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return _serialize_api_key(key)

    async def delete(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> DeleteResponse:
        """Deletes an API key record."""
        await self.service.delete_key(
            db=db,
            api_key_id=api_key_id,
            performed_by_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return DeleteResponse(
            success=True, message=f"API Key {api_key_id} successfully deleted."
        )

    async def copy(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> DeleteResponse:
        """Records a copy action in the audit history."""
        await self.service.copy_key(
            db=db,
            api_key_id=api_key_id,
            performed_by_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return DeleteResponse(success=True, message="API Key copy recorded.")

    async def get_usage(
        self, db: AsyncSession, api_key_id: uuid.UUID
    ) -> ApiKeyUsageStatsResponse:
        """Returns analytics summaries and histories for a key."""
        stats = await self.service.get_usage_analytics(db, api_key_id)
        return ApiKeyUsageStatsResponse(
            requests_today=stats["requests_today"],
            requests_this_month=stats["requests_this_month"],
            failed_requests=stats["failed_requests"],
            successful_requests=stats["successful_requests"],
            last_used_at=stats["last_used_at"].isoformat() if stats["last_used_at"] else None,
            top_endpoint=stats["top_endpoint"],
            recent_usages=[_serialize_usage(u) for u in stats["recent_usages"]],
            audit_history=[_serialize_audit(a) for a in stats["audit_history"]],
        )

    async def list_audits(
        self, db: AsyncSession, api_key_id: uuid.UUID
    ) -> ApiKeyAuditListResponse:
        """Returns audit history for the key."""
        audits = await self.service.get_audit_history(db, api_key_id)
        return ApiKeyAuditListResponse(
            results=[_serialize_audit(a) for a in audits],
            total=len(audits),
        )
