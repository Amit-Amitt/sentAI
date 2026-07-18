"""Service layer for Organization business logic."""

import uuid
from typing import List, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.exceptions import EntityNotFoundException, ValidationException
from sentinel_api.models.enums import MemberRole
from sentinel_api.models.organization import Organization
from sentinel_api.repositories.membership import MembershipRepository
from sentinel_api.repositories.organization import OrganizationRepository
from sentinel_api.repositories.workspace import WorkspaceRepository

logger = structlog.get_logger("sentinel_api.services.organization")


class OrganizationService:
    """Orchestrates organization lifecycle — create, update, delete, list."""

    def __init__(self) -> None:
        self.org_repo = OrganizationRepository()
        self.membership_repo = MembershipRepository()
        self.workspace_repo = WorkspaceRepository()

    async def create_organization(
        self,
        db: AsyncSession,
        name: str,
        slug: str,
        owner_id: uuid.UUID,
        industry: Optional[str] = None,
        region: Optional[str] = None,
        timezone: str = "UTC",
    ) -> Organization:
        """Creates a new organization with owner membership and a default workspace."""
        # Check slug uniqueness
        existing = await self.org_repo.get_by_slug(db, slug)
        if existing:
            raise ValidationException(
                f"Organization with slug '{slug}' already exists.",
                error_code="ORG_SLUG_TAKEN",
                status_code=409,
            )

        org = await self.org_repo.create(
            db=db,
            name=name,
            slug=slug,
            owner_id=owner_id,
            industry=industry,
            region=region,
            timezone=timezone,
        )
        logger.info("Organization created", org_id=str(org.id), slug=slug)

        # Auto-create owner membership
        await self.membership_repo.create(
            db=db,
            user_id=owner_id,
            organization_id=org.id,
            role=MemberRole.OWNER.value,
        )
        logger.info("Owner membership created", org_id=str(org.id))

        # Auto-create default workspace
        await self.workspace_repo.create(
            db=db,
            name="Default",
            slug="default",
            organization_id=org.id,
            environment="development",
            description="Default workspace created automatically.",
        )
        logger.info("Default workspace created", org_id=str(org.id))

        return org

    async def get_organization(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> Organization:
        """Retrieves an organization by ID or raises 404."""
        org = await self.org_repo.get_by_id(db, org_id)
        if not org:
            raise EntityNotFoundException(
                f"Organization not found: {org_id}",
                error_code="ORG_NOT_FOUND",
            )
        return org

    async def list_user_organizations(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> List[Organization]:
        """Lists all organizations a user belongs to."""
        return await self.org_repo.list_by_user(db, user_id)

    async def update_organization(
        self,
        db: AsyncSession,
        org_id: uuid.UUID,
        **kwargs: object,
    ) -> Organization:
        """Updates organization fields."""
        org = await self.get_organization(db, org_id)
        org = await self.org_repo.update(db, org, **kwargs)
        logger.info("Organization updated", org_id=str(org_id))
        return org

    async def delete_organization(
        self, db: AsyncSession, org_id: uuid.UUID
    ) -> bool:
        """Deletes an organization and all cascaded resources."""
        org = await self.get_organization(db, org_id)
        await self.org_repo.delete(db, org)
        logger.info("Organization deleted", org_id=str(org_id))
        return True
