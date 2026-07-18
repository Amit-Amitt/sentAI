"""Service layer for Workspace business logic."""

import uuid
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.exceptions import EntityNotFoundException, ValidationException
from sentinel_api.models.workspace import Workspace
from sentinel_api.repositories.workspace import WorkspaceRepository

logger = structlog.get_logger("sentinel_api.services.workspace")


class WorkspaceService:
    """Orchestrates workspace lifecycle — create, update, delete, list."""

    VALID_ENVIRONMENTS = {"development", "staging", "production"}

    def __init__(self) -> None:
        self.repo = WorkspaceRepository()

    async def create_workspace(
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
        """Creates a new workspace within an organization."""
        if environment not in self.VALID_ENVIRONMENTS:
            raise ValidationException(
                f"Invalid environment: {environment}. Must be one of: {', '.join(self.VALID_ENVIRONMENTS)}",
                error_code="INVALID_ENVIRONMENT",
            )

        # Check uniqueness of slug within org
        existing = await self.repo.list_by_organization(db, organization_id)
        if any(ws.slug == slug for ws in existing):
            raise ValidationException(
                f"Workspace with slug '{slug}' already exists in this organization.",
                error_code="WORKSPACE_SLUG_TAKEN",
                status_code=409,
            )

        ws = await self.repo.create(
            db=db,
            name=name,
            slug=slug,
            organization_id=organization_id,
            environment=environment,
            description=description,
            ai_config=ai_config,
            incident_retention_days=incident_retention_days,
        )
        logger.info("Workspace created", ws_id=str(ws.id), slug=slug)
        return ws

    async def get_workspace(
        self, db: AsyncSession, ws_id: uuid.UUID
    ) -> Workspace:
        """Retrieves a workspace by ID or raises 404."""
        ws = await self.repo.get_by_id(db, ws_id)
        if not ws:
            raise EntityNotFoundException(
                f"Workspace not found: {ws_id}",
                error_code="WORKSPACE_NOT_FOUND",
            )
        return ws

    async def list_workspaces(
        self, db: AsyncSession, organization_id: uuid.UUID
    ) -> List[Workspace]:
        """Lists all workspaces within an organization."""
        return await self.repo.list_by_organization(db, organization_id)

    async def update_workspace(
        self,
        db: AsyncSession,
        ws_id: uuid.UUID,
        **kwargs: object,
    ) -> Workspace:
        """Updates workspace settings."""
        ws = await self.get_workspace(db, ws_id)

        # Validate environment if being changed
        if "environment" in kwargs and kwargs["environment"] is not None:
            env = kwargs["environment"]
            if env not in self.VALID_ENVIRONMENTS:
                raise ValidationException(
                    f"Invalid environment: {env}",
                    error_code="INVALID_ENVIRONMENT",
                )

        ws = await self.repo.update(db, ws, **kwargs)
        logger.info("Workspace updated", ws_id=str(ws_id))
        return ws

    async def delete_workspace(
        self, db: AsyncSession, ws_id: uuid.UUID
    ) -> bool:
        """Deletes a workspace."""
        ws = await self.get_workspace(db, ws_id)
        await self.repo.delete(db, ws)
        logger.info("Workspace deleted", ws_id=str(ws_id))
        return True
