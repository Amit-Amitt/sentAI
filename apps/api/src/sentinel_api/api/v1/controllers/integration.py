"""Controller layer orchestration for integrations API."""

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.schemas.integration import (
    WorkspaceIntegrationCreate,
    WorkspaceIntegrationUpdate,
)
from sentinel_api.services.integration import IntegrationService


class IntegrationController:
    """Controller orchestrator managing routing requests for Integrations."""

    def __init__(self) -> None:
        self.service = IntegrationService()

    async def list_providers(
        self, db: AsyncSession, workspace_id: Optional[uuid.UUID]
    ) -> List[Dict[str, Any]]:
        """Invokes provider listing matching current active connection states."""
        return await self.service.list_providers_with_connections(db, workspace_id)

    async def get_provider(
        self, db: AsyncSession, provider_id: uuid.UUID, workspace_id: Optional[uuid.UUID]
    ) -> Dict[str, Any]:
        """Queries detailed specifications for a single integration provider."""
        return await self.service.get_provider_details(db, provider_id, workspace_id)

    async def connect(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        payload: WorkspaceIntegrationCreate,
        current_user_id: Optional[uuid.UUID] = None,
        client_host: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Any:
        """Invokes remote tests and provisions database configuration structures."""
        return await self.service.connect_integration(
            db,
            workspace_id=workspace_id,
            provider_id=payload.provider_id,
            config=payload.config,
            credentials=payload.credentials,
            current_user_id=current_user_id,
            client_host=client_host,
            user_agent=user_agent,
        )

    async def update(
        self,
        db: AsyncSession,
        connection_id: uuid.UUID,
        workspace_id: uuid.UUID,
        payload: WorkspaceIntegrationUpdate,
        current_user_id: Optional[uuid.UUID] = None,
        client_host: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Any:
        """Updates integration properties, configs, secrets, or toggles state."""
        return await self.service.update_connection_settings(
            db,
            connection_id=connection_id,
            workspace_id=workspace_id,
            config=payload.config,
            credentials=payload.credentials,
            is_enabled=payload.is_enabled,
            current_user_id=current_user_id,
            client_host=client_host,
            user_agent=user_agent,
        )

    async def disconnect(
        self,
        db: AsyncSession,
        connection_id: uuid.UUID,
        workspace_id: uuid.UUID,
        current_user_id: Optional[uuid.UUID] = None,
        client_host: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Any:
        """Sets connection config status to disconnected."""
        return await self.service.disconnect_integration(
            db,
            connection_id=connection_id,
            workspace_id=workspace_id,
            current_user_id=current_user_id,
            client_host=client_host,
            user_agent=user_agent,
        )

    async def delete(
        self,
        db: AsyncSession,
        connection_id: uuid.UUID,
        workspace_id: uuid.UUID,
        current_user_id: Optional[uuid.UUID] = None,
        client_host: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Purges connection settings records completely."""
        return await self.service.delete_integration_permanently(
            db,
            connection_id=connection_id,
            workspace_id=workspace_id,
            current_user_id=current_user_id,
            client_host=client_host,
            user_agent=user_agent,
        )

    async def test(
        self, db: AsyncSession, connection_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Tests active credential keys against mock remote systems."""
        return await self.service.test_connection_health(db, connection_id, workspace_id)

    async def sync(
        self, db: AsyncSession, connection_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Launches a simulated synchronization run, returning status log metadata."""
        return await self.service.trigger_manual_sync(db, connection_id, workspace_id)

    async def get_history(
        self, db: AsyncSession, connection_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Fetches consolidated sync runs and config edit logs."""
        return await self.service.get_history_logs(db, connection_id, workspace_id)
