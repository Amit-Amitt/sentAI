"""Repository for Integration entity database operations."""

import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sentinel_api.models.integration import (
    IntegrationProvider,
    WorkspaceIntegration,
    IntegrationCredential,
    IntegrationWebhook,
    IntegrationSync,
    IntegrationAudit,
)


class IntegrationRepository:
    """Data access layer for Integration entities."""

    # ----------------------------------------------------
    # Integration Provider Operations
    # ----------------------------------------------------

    async def get_provider_by_id(
        self, db: AsyncSession, provider_id: uuid.UUID
    ) -> Optional[IntegrationProvider]:
        """Retrieves an integration provider by ID."""
        result = await db.execute(
            select(IntegrationProvider).where(IntegrationProvider.id == provider_id)
        )
        return result.scalars().first()

    async def get_provider_by_key(
        self, db: AsyncSession, key: str
    ) -> Optional[IntegrationProvider]:
        """Retrieves an integration provider by its key slug."""
        result = await db.execute(
            select(IntegrationProvider).where(IntegrationProvider.key == key)
        )
        return result.scalars().first()

    async def list_providers(self, db: AsyncSession) -> List[IntegrationProvider]:
        """Lists all supported integration providers."""
        result = await db.execute(
            select(IntegrationProvider).order_by(IntegrationProvider.name.asc())
        )
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Workspace Connection Operations
    # ----------------------------------------------------

    async def get_connection_by_id(
        self, db: AsyncSession, connection_id: uuid.UUID
    ) -> Optional[WorkspaceIntegration]:
        """Retrieves a workspace integration connection by ID."""
        result = await db.execute(
            select(WorkspaceIntegration)
            .where(WorkspaceIntegration.id == connection_id)
            .options(
                selectinload(WorkspaceIntegration.provider),
                selectinload(WorkspaceIntegration.credentials),
                selectinload(WorkspaceIntegration.webhooks),
            )
        )
        return result.scalars().first()

    async def get_connection_by_provider(
        self, db: AsyncSession, workspace_id: uuid.UUID, provider_id: uuid.UUID
    ) -> Optional[WorkspaceIntegration]:
        """Retrieves connection configuration for a specific provider in a workspace."""
        result = await db.execute(
            select(WorkspaceIntegration)
            .where(
                WorkspaceIntegration.workspace_id == workspace_id,
                WorkspaceIntegration.provider_id == provider_id,
            )
            .options(
                selectinload(WorkspaceIntegration.provider),
                selectinload(WorkspaceIntegration.credentials),
                selectinload(WorkspaceIntegration.webhooks),
            )
        )
        return result.scalars().first()

    async def list_workspace_connections(
        self, db: AsyncSession, workspace_id: uuid.UUID
    ) -> List[WorkspaceIntegration]:
        """Lists all active or configured integrations in a workspace."""
        result = await db.execute(
            select(WorkspaceIntegration)
            .where(WorkspaceIntegration.workspace_id == workspace_id)
            .options(
                selectinload(WorkspaceIntegration.provider),
                selectinload(WorkspaceIntegration.credentials),
                selectinload(WorkspaceIntegration.webhooks),
            )
            .order_by(WorkspaceIntegration.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_connection(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        provider_id: uuid.UUID,
        config: Dict[str, Any],
        status: str = "connected",
        is_enabled: bool = True,
        error_message: Optional[str] = None,
    ) -> WorkspaceIntegration:
        """Establishes a new connection record between workspace and provider."""
        conn = WorkspaceIntegration(
            workspace_id=workspace_id,
            provider_id=provider_id,
            config=config,
            status=status,
            is_enabled=is_enabled,
            error_message=error_message,
        )
        db.add(conn)
        await db.flush()

        # Eagerly load relationship before returning
        return await self.get_connection_by_id(db, conn.id)

    async def update_connection(
        self,
        db: AsyncSession,
        connection: WorkspaceIntegration,
        **kwargs: object,
    ) -> WorkspaceIntegration:
        """Updates WorkspaceIntegration fields."""
        for key, value in kwargs.items():
            if hasattr(connection, key) and value is not None:
                setattr(connection, key, value)
        await db.flush()
        return await self.get_connection_by_id(db, connection.id)

    async def delete_connection(
        self, db: AsyncSession, connection: WorkspaceIntegration
    ) -> bool:
        """Removes a workspace integration configuration and its children."""
        await db.delete(connection)
        await db.flush()
        return True

    # ----------------------------------------------------
    # Credentials Operations
    # ----------------------------------------------------

    async def create_credential(
        self,
        db: AsyncSession,
        workspace_integration_id: uuid.UUID,
        credential_type: str,
        key: str,
        value: str,
        expires_at: Optional[datetime] = None,
    ) -> IntegrationCredential:
        """Persists a secure credential string related to the connection."""
        cred = IntegrationCredential(
            workspace_integration_id=workspace_integration_id,
            credential_type=credential_type,
            key=key,
            value=value,
            expires_at=expires_at,
        )
        db.add(cred)
        await db.flush()
        return cred

    async def delete_connection_credentials(
        self, db: AsyncSession, workspace_integration_id: uuid.UUID
    ) -> None:
        """Clears all cached credentials for a connection (e.g. before rotate/update)."""
        result = await db.execute(
            select(IntegrationCredential).where(
                IntegrationCredential.workspace_integration_id == workspace_integration_id
            )
        )
        for cred in result.scalars().all():
            await db.delete(cred)
        await db.flush()

    # ----------------------------------------------------
    # Webhook Operations
    # ----------------------------------------------------

    async def create_webhook(
        self,
        db: AsyncSession,
        workspace_integration_id: uuid.UUID,
        name: str,
        url: str,
        direction: str = "incoming",
        secret: Optional[str] = None,
        retry_strategy: Optional[Dict[str, Any]] = None,
        status: str = "active",
    ) -> IntegrationWebhook:
        """Registers a telemetry webhook receiver or dispatcher."""
        webhook = IntegrationWebhook(
            workspace_integration_id=workspace_integration_id,
            name=name,
            url=url,
            direction=direction,
            secret=secret,
            retry_strategy=retry_strategy or {"max_retries": 3, "backoff": "exponential"},
            status=status,
        )
        db.add(webhook)
        await db.flush()
        return webhook

    # ----------------------------------------------------
    # Sync Operations
    # ----------------------------------------------------

    async def create_sync(
        self,
        db: AsyncSession,
        workspace_integration_id: uuid.UUID,
        status: str,
        duration_ms: int = 0,
        imported_resources: int = 0,
        errors: Optional[List[Any]] = None,
        warnings: Optional[List[Any]] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> IntegrationSync:
        """Appends a new integration sync history record."""
        sync = IntegrationSync(
            workspace_integration_id=workspace_integration_id,
            status=status,
            started_at=started_at or datetime.now(UTC),
            completed_at=completed_at or datetime.now(UTC),
            duration_ms=duration_ms,
            imported_resources=imported_resources,
            errors=errors or [],
            warnings=warnings or [],
        )
        db.add(sync)
        await db.flush()
        return sync

    async def get_sync_history(
        self, db: AsyncSession, workspace_integration_id: uuid.UUID, limit: int = 50
    ) -> List[IntegrationSync]:
        """Retrieves chronological sync events for an integration connection."""
        result = await db.execute(
            select(IntegrationSync)
            .where(IntegrationSync.workspace_integration_id == workspace_integration_id)
            .order_by(IntegrationSync.started_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # ----------------------------------------------------
    # Audit Log Operations
    # ----------------------------------------------------

    async def create_audit(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        workspace_integration_id: Optional[uuid.UUID],
        action: str,
        performed_by_id: Optional[uuid.UUID],
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> IntegrationAudit:
        """Creates an audit trail log for integration management events."""
        audit = IntegrationAudit(
            workspace_id=workspace_id,
            workspace_integration_id=workspace_integration_id,
            action=action,
            performed_by_id=performed_by_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(UTC),
        )
        db.add(audit)
        await db.flush()
        return audit

    async def get_audit_history(
        self, db: AsyncSession, workspace_id: uuid.UUID, workspace_integration_id: Optional[uuid.UUID] = None, limit: int = 100
    ) -> List[IntegrationAudit]:
        """Fetches management actions executed on integrations."""
        stmt = select(IntegrationAudit).where(IntegrationAudit.workspace_id == workspace_id)
        if workspace_integration_id is not None:
            stmt = stmt.where(IntegrationAudit.workspace_integration_id == workspace_integration_id)
        stmt = stmt.order_by(IntegrationAudit.timestamp.desc()).limit(limit)

        result = await db.execute(stmt)
        return list(result.scalars().all())
