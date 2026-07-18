import uuid
from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.dependencies.current_user import get_current_user
from sentinel_api.api.v1.dependencies.services import get_membership_service
from sentinel_api.database.session import get_db_session
from sentinel_api.models.user import User
from sentinel_api.services.membership import MembershipService


def require_permission(permission_name: str) -> Callable:
    """Dependency factory enforcing database-backed permissions for a specific organization."""

    async def dependency(
        org_id: uuid.UUID,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session),
        membership_service: MembershipService = Depends(get_membership_service),
    ) -> User:
        has_perm = await membership_service.check_permission(
            db=db,
            user_id=user.id,
            organization_id=org_id,
            permission_name=permission_name,
        )
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Missing permission '{permission_name}'",
            )
        return user

    return dependency


def require_role(role_name: str) -> Callable:
    """Dependency factory enforcing specific roles for an organization."""

    async def dependency(
        org_id: uuid.UUID,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session),
        membership_service: MembershipService = Depends(get_membership_service),
    ) -> User:
        user_role = await membership_service.get_user_role(
            db=db, user_id=user.id, organization_id=org_id
        )
        if not user_role or user_role != role_name.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Requires role '{role_name}'",
            )
        return user

    return dependency
