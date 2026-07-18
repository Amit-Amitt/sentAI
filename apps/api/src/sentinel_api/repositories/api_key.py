"""Repository for API Key entity database operations."""

import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sentinel_api.models.api_key import ApiKey, ApiKeyAudit, ApiKeyPermission, ApiKeyUsage


class ApiKeyRepository:
    """Data access layer for ApiKey and related entities."""

    async def create(
        self,
        db: AsyncSession,
        name: str,
        prefix: str,
        secret_hash: str,
        environment: str,
        workspace_id: uuid.UUID,
        created_by_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        scopes: Optional[List[str]] = None,
    ) -> ApiKey:
        """Creates a new API Key with initial permissions."""
        perms = [ApiKeyPermission(scope=s) for s in (scopes or [])]

        api_key = ApiKey(
            name=name,
            prefix=prefix,
            secret_hash=secret_hash,
            environment=environment,
            workspace_id=workspace_id,
            created_by_id=created_by_id,
            description=description,
            expires_at=expires_at,
            status="active",
            permissions=perms,
        )
        db.add(api_key)
        await db.flush()

        # Eagerly load relationship before returning
        result = await db.execute(
            select(ApiKey)
            .where(ApiKey.id == api_key.id)
            .options(selectinload(ApiKey.permissions))
        )
        return result.scalars().one()

    async def get_by_id(
        self, db: AsyncSession, api_key_id: uuid.UUID
    ) -> Optional[ApiKey]:
        """Retrieves an API Key by primary key."""
        result = await db.execute(
            select(ApiKey)
            .where(ApiKey.id == api_key_id)
            .options(selectinload(ApiKey.permissions))
        )
        return result.scalars().first()

    async def get_audits(
        self, db: AsyncSession, api_key_id: uuid.UUID
    ) -> List[ApiKeyAudit]:
        """Returns audit rows for a key, newest first."""
        result = await db.execute(
            select(ApiKeyAudit)
            .where(ApiKeyAudit.api_key_id == api_key_id)
            .options(selectinload(ApiKeyAudit.performed_by))
            .order_by(ApiKeyAudit.timestamp.desc())
        )
        return list(result.scalars().all())

    async def get_by_hash(self, db: AsyncSession, secret_hash: str) -> Optional[ApiKey]:
        """Retrieves an API Key by its SHA-256 secret hash."""
        result = await db.execute(
            select(ApiKey)
            .where(ApiKey.secret_hash == secret_hash)
            .options(selectinload(ApiKey.permissions))
        )
        return result.scalars().first()

    async def list_by_workspace(
        self, db: AsyncSession, workspace_id: uuid.UUID
    ) -> List[ApiKey]:
        """Lists all API keys configured within a specific workspace."""
        result = await db.execute(
            select(ApiKey)
            .where(ApiKey.workspace_id == workspace_id)
            .options(selectinload(ApiKey.permissions))
            .order_by(ApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(
        self,
        db: AsyncSession,
        api_key: ApiKey,
        scopes: Optional[List[str]] = None,
        **kwargs: object,
    ) -> ApiKey:
        """Updates API Key fields and manages scope updates."""
        for key, value in kwargs.items():
            if hasattr(api_key, key) and value is not None:
                setattr(api_key, key, value)
        await db.flush()

        # Update scopes if provided
        if scopes is not None:
            # Delete old permissions
            for perm in list(api_key.permissions):
                await db.delete(perm)
            await db.flush()

            # Add new permissions and update relationship
            new_perms = []
            for scope in scopes:
                perm = ApiKeyPermission(api_key_id=api_key.id, scope=scope)
                db.add(perm)
                new_perms.append(perm)
            api_key.permissions = new_perms
            await db.flush()

        # Eagerly load relationship before returning updated state
        result = await db.execute(
            select(ApiKey)
            .where(ApiKey.id == api_key.id)
            .options(selectinload(ApiKey.permissions))
        )
        return result.scalars().one()

    async def delete(self, db: AsyncSession, api_key: ApiKey) -> bool:
        """Deletes an API Key record and its child relations."""
        await db.delete(api_key)
        await db.flush()
        return True

    async def create_usage(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ApiKeyUsage:
        """Appends a new usage transaction record and updates the API Key's last used timestamp."""
        usage = ApiKeyUsage(
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(UTC),
        )
        db.add(usage)

        # Update API Key last used timestamp
        result = await db.execute(select(ApiKey).where(ApiKey.id == api_key_id))
        api_key = result.scalars().first()
        if api_key:
            api_key.last_used_at = datetime.now(UTC)

        await db.flush()
        return usage

    async def create_audit(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        action: str,
        performed_by_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> ApiKeyAudit:
        """Creates an audit log event associated with the API Key."""
        audit = ApiKeyAudit(
            api_key_id=api_key_id,
            action=action,
            performed_by_id=performed_by_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            timestamp=datetime.now(UTC),
        )
        db.add(audit)
        await db.flush()
        return audit

    async def get_usage_statistics(
        self, db: AsyncSession, api_key_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Aggregates transactional and audit analytics for a given API Key."""
        now = datetime.now(UTC)
        start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Requests Today count
        today_res = await db.execute(
            select(func.count(ApiKeyUsage.id)).where(
                ApiKeyUsage.api_key_id == api_key_id,
                ApiKeyUsage.timestamp >= start_of_today,
            )
        )
        requests_today = today_res.scalar() or 0

        # Requests This Month count
        month_res = await db.execute(
            select(func.count(ApiKeyUsage.id)).where(
                ApiKeyUsage.api_key_id == api_key_id,
                ApiKeyUsage.timestamp >= start_of_month,
            )
        )
        requests_this_month = month_res.scalar() or 0

        # Successful vs Failed requests counts
        success_res = await db.execute(
            select(func.count(ApiKeyUsage.id)).where(
                ApiKeyUsage.api_key_id == api_key_id,
                ApiKeyUsage.status_code < 400,
            )
        )
        successful_requests = success_res.scalar() or 0

        failed_res = await db.execute(
            select(func.count(ApiKeyUsage.id)).where(
                ApiKeyUsage.api_key_id == api_key_id,
                ApiKeyUsage.status_code >= 400,
            )
        )
        failed_requests = failed_res.scalar() or 0

        # Top Endpoint
        top_endpoint_stmt = (
            select(ApiKeyUsage.endpoint, func.count(ApiKeyUsage.id).label("cnt"))
            .where(ApiKeyUsage.api_key_id == api_key_id)
            .group_by(ApiKeyUsage.endpoint)
            .order_by(func.count(ApiKeyUsage.id).desc())
            .limit(1)
        )
        top_endpoint_res = await db.execute(top_endpoint_stmt)
        top_endpoint_row = top_endpoint_res.first()
        top_endpoint = top_endpoint_row[0] if top_endpoint_row else None

        # Fetch last 50 usages
        usages_res = await db.execute(
            select(ApiKeyUsage)
            .where(ApiKeyUsage.api_key_id == api_key_id)
            .order_by(ApiKeyUsage.timestamp.desc())
            .limit(50)
        )
        recent_usages = list(usages_res.scalars().all())

        # Fetch full audit log history
        audit_history = await self.get_audits(db, api_key_id)

        # Get API Key last used timestamp
        key_res = await db.execute(select(ApiKey.last_used_at).where(ApiKey.id == api_key_id))
        last_used_at = key_res.scalar()

        return {
            "requests_today": requests_today,
            "requests_this_month": requests_this_month,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "top_endpoint": top_endpoint,
            "last_used_at": last_used_at,
            "recent_usages": recent_usages,
            "audit_history": audit_history,
        }
