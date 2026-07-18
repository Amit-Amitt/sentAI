"""Service layer for Membership business logic."""

import uuid
from typing import List, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.exceptions import EntityNotFoundException, ValidationException
from sentinel_api.models.enums import MemberRole, Permission, has_permission
from sentinel_api.models.membership import Membership
from sentinel_api.repositories.membership import MembershipRepository
from sentinel_api.repositories.user import UserRepository

logger = structlog.get_logger("sentinel_api.services.membership")


class MembershipService:
    """Orchestrates membership lifecycle — add, update, remove, permission checks."""

    VALID_ROLES = {r.value for r in MemberRole}

    def __init__(self) -> None:
        self.membership_repo = MembershipRepository()
        self.user_repo = UserRepository()

    async def add_member(
        self,
        db: AsyncSession,
        email: str,
        organization_id: uuid.UUID,
        role: str = "engineer",
    ) -> Membership:
        """Adds a user to an organization by email."""
        if role not in self.VALID_ROLES:
            raise ValidationException(
                f"Invalid role: {role}. Must be one of: {', '.join(self.VALID_ROLES)}",
                error_code="INVALID_ROLE",
            )

        user = await self.user_repo.get_by_email(db, email)
        if not user:
            raise EntityNotFoundException(
                f"User not found with email: {email}",
                error_code="USER_NOT_FOUND",
            )

        # Check if already a member
        existing = await self.membership_repo.get_by_user_and_org(
            db, user.id, organization_id
        )
        if existing:
            raise ValidationException(
                f"User {email} is already a member of this organization.",
                error_code="ALREADY_MEMBER",
                status_code=409,
            )

        membership = await self.membership_repo.create(
            db=db,
            user_id=user.id,
            organization_id=organization_id,
            role=role,
        )
        logger.info(
            "Member added",
            user_id=str(user.id),
            org_id=str(organization_id),
            role=role,
        )
        return membership

    async def list_members(
        self, db: AsyncSession, organization_id: uuid.UUID
    ) -> List[Membership]:
        """Lists all org-level members."""
        return await self.membership_repo.list_by_org(db, organization_id)

    async def update_role(
        self,
        db: AsyncSession,
        membership_id: uuid.UUID,
        role: str,
    ) -> Membership:
        """Updates the role of an existing membership."""
        if role not in self.VALID_ROLES:
            raise ValidationException(
                f"Invalid role: {role}",
                error_code="INVALID_ROLE",
            )

        membership = await self.membership_repo.get(db, membership_id)
        if not membership:
            raise EntityNotFoundException(
                f"Membership not found: {membership_id}",
                error_code="MEMBERSHIP_NOT_FOUND",
            )

        membership = await self.membership_repo.update_role(db, membership, role)
        logger.info("Member role updated", membership_id=str(membership_id), role=role)
        return membership

    async def remove_member(
        self, db: AsyncSession, membership_id: uuid.UUID
    ) -> bool:
        """Removes a member from an organization."""
        membership = await self.membership_repo.get(db, membership_id)
        if not membership:
            raise EntityNotFoundException(
                f"Membership not found: {membership_id}",
                error_code="MEMBERSHIP_NOT_FOUND",
            )

        # Prevent removing the last owner
        if membership.role == MemberRole.OWNER.value:
            org_members = await self.membership_repo.list_by_org(
                db, membership.organization_id
            )
            owner_count = sum(
                1 for m in org_members if m.role == MemberRole.OWNER.value
            )
            if owner_count <= 1:
                raise ValidationException(
                    "Cannot remove the last owner of an organization.",
                    error_code="LAST_OWNER",
                )

        await self.membership_repo.delete(db, membership)
        logger.info("Member removed", membership_id=str(membership_id))
        return True

    async def check_permission(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        permission: Permission,
    ) -> bool:
        """Checks if a user has a specific permission in an organization."""
        membership = await self.membership_repo.get_by_user_and_org(
            db, user_id, organization_id
        )
        if not membership:
            return False
        return has_permission(MemberRole(membership.role), permission)

    async def get_user_role(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[str]:
        """Returns the user's role in an organization, or None."""
        membership = await self.membership_repo.get_by_user_and_org(
            db, user_id, organization_id
        )
        return membership.role if membership else None
