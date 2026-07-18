import uuid
from typing import List, Optional, Sequence, Tuple

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.exceptions import EntityNotFoundException, ValidationException
from sentinel_api.models.organization_member import OrganizationMember
from sentinel_api.repositories.membership import MembershipRepository
from sentinel_api.repositories.user import UserRepository
from sentinel_api.repositories.organization import OrganizationRepository
from sentinel_api.services.activity import ActivityService

logger = structlog.get_logger("sentinel_api.services.membership")


class MembershipService:
    """Orchestrates team collaboration member workflows, role management, and RBAC."""

    VALID_ROLES = {"owner", "admin", "engineer", "viewer"}

    def __init__(self) -> None:
        self.membership_repo = MembershipRepository()
        self.user_repo = UserRepository()
        self.org_repo = OrganizationRepository()
        self.activity_service = ActivityService()

    async def add_member(
        self,
        db: AsyncSession,
        email: str,
        organization_id: uuid.UUID,
        role: str = "engineer",
        actor_id: Optional[uuid.UUID] = None,
    ) -> OrganizationMember:
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

        member = await self.membership_repo.create(
            db=db,
            user_id=user.id,
            organization_id=organization_id,
            role=role,
            status="active",
        )

        await self.activity_service.log_activity(
            db=db,
            organization_id=organization_id,
            user_id=actor_id,
            action="member_added",
            details={
                "target_user_id": str(user.id),
                "target_email": email,
                "role": role,
            },
        )

        logger.info(
            "Member added to organization",
            user_id=str(user.id),
            org_id=str(organization_id),
            role=role,
        )
        return member

    async def list_members(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        search: Optional[str] = None,
        role_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[Sequence[OrganizationMember], int]:
        """Lists team members with search, role filters, and pagination support."""
        members = await self.membership_repo.list_by_org(
            db, organization_id, search, role_filter, limit, offset
        )
        total = await self.membership_repo.count_by_org(
            db, organization_id, search, role_filter
        )
        return members, total

    async def update_role(
        self,
        db: AsyncSession,
        membership_id: uuid.UUID,
        role: str,
        actor_id: uuid.UUID,
    ) -> OrganizationMember:
        """Updates the role of a team member (Owner role protected)."""
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

        # Protect Owner role
        if role == "owner":
            raise ValidationException(
                "Cannot update a member's role to 'owner' directly. Use ownership transfer instead.",
                error_code="OWNER_ROLE_PROTECTED",
            )

        # If current role is owner, prevent demoting self without transfer
        if membership.role.name == "owner":
            raise ValidationException(
                "Cannot demote the owner of an organization. Transfer ownership to another user first.",
                error_code="OWNER_DEMOTION_FORBIDDEN",
            )

        old_role = membership.role.name
        membership = await self.membership_repo.update_role(db, membership, role)

        await self.activity_service.log_activity(
            db=db,
            organization_id=membership.organization_id,
            user_id=actor_id,
            action="role_changed",
            details={
                "target_member_id": str(membership_id),
                "target_user_id": str(membership.user_id),
                "old_role": old_role,
                "new_role": role,
            },
        )

        logger.info(
            "Member role updated",
            membership_id=str(membership_id),
            old_role=old_role,
            new_role=role,
        )
        return membership

    async def remove_member(
        self, db: AsyncSession, membership_id: uuid.UUID, actor_id: uuid.UUID
    ) -> bool:
        """Removes a member from an organization."""
        membership = await self.membership_repo.get(db, membership_id)
        if not membership:
            raise EntityNotFoundException(
                f"Membership not found: {membership_id}",
                error_code="MEMBERSHIP_NOT_FOUND",
            )

        # Prevent removing the Owner
        if membership.role.name == "owner":
            raise ValidationException(
                "Cannot remove the owner of an organization. Transfer ownership first.",
                error_code="OWNER_REMOVAL_FORBIDDEN",
            )

        org_id = membership.organization_id
        target_user_id = membership.user_id
        target_email = membership.user.email

        await self.membership_repo.delete(db, membership)

        await self.activity_service.log_activity(
            db=db,
            organization_id=org_id,
            user_id=actor_id,
            action="member_removed",
            details={
                "target_user_id": str(target_user_id),
                "target_email": target_email,
            },
        )

        logger.info("Member removed", membership_id=str(membership_id))
        return True

    async def transfer_ownership(
        self,
        db: AsyncSession,
        organization_id: uuid.UUID,
        target_member_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> OrganizationMember:
        """Transfers organization ownership to a target member."""
        org = await self.org_repo.get_by_id(db, organization_id)
        if not org:
            raise EntityNotFoundException("Organization not found.")

        # Confirm the actor is the current owner
        if org.owner_id != actor_id:
            raise ValidationException(
                "Only the current owner can transfer organization ownership.",
                error_code="NOT_OWNER",
                status_code=403,
            )

        target_member = await self.membership_repo.get(db, target_member_id)
        if not target_member or target_member.organization_id != organization_id:
            raise EntityNotFoundException("Target member not found in this organization.")

        if target_member.user_id == actor_id:
            raise ValidationException(
                "Cannot transfer ownership to yourself.",
                error_code="SELF_TRANSFER_FORBIDDEN",
            )

        # Resolve current owner member record
        current_owner_member = await self.membership_repo.get_by_user_and_org(
            db, actor_id, organization_id
        )

        # 1. Update target role to Owner
        target_member = await self.membership_repo.update_role(db, target_member, "owner")

        # 2. Update previous owner role to Admin
        if current_owner_member:
            await self.membership_repo.update_role(db, current_owner_member, "admin")

        # 3. Update organization owner_id field
        org.owner_id = target_member.user_id

        await self.activity_service.log_activity(
            db=db,
            organization_id=organization_id,
            user_id=actor_id,
            action="ownership_transferred",
            details={
                "previous_owner_id": str(actor_id),
                "new_owner_id": str(target_member.user_id),
                "new_owner_email": target_member.user.email,
            },
        )

        await db.flush()
        logger.info(
            "Ownership transferred",
            org_id=str(organization_id),
            from_user=str(actor_id),
            to_user=str(target_member.user_id),
        )
        return target_member

    async def check_permission(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        organization_id: uuid.UUID,
        permission_name: str,
    ) -> bool:
        """Dynamic database-driven permission verification hook."""
        membership = await self.membership_repo.get_by_user_and_org(
            db, user_id, organization_id
        )
        if not membership:
            return False

        # Load role and check permissions list
        role = membership.role
        for perm in role.permissions:
            if perm.name == "full_access" or perm.name == permission_name:
                return True

        return False

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
        return membership.role.name if membership else None
