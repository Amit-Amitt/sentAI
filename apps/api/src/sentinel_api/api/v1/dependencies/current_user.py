"""Mock current user dependency — provides a seed user until auth is implemented."""

import uuid
from typing import Optional

import structlog
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.database.session import get_db_session
from sentinel_api.models.user import User
from sentinel_api.repositories.user import UserRepository

logger = structlog.get_logger("sentinel_api.dependencies.current_user")

# Fixed seed user ID for deterministic development
SEED_USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
SEED_USER_EMAIL = "admin@sentinel.ai"
SEED_USER_NAME = "Sentinel Admin"

_user_repo = UserRepository()


async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Returns the current authenticated user.

    Until auth is implemented, this creates/returns a deterministic seed user
    so multi-tenancy features work end-to-end. When auth is built, only this
    dependency needs to be swapped.
    """
    user = await _user_repo.get_by_email(db, SEED_USER_EMAIL)
    if user:
        return user

    # First-time seed: create the mock user
    user = User(
        id=SEED_USER_ID,
        email=SEED_USER_EMAIL,
        full_name=SEED_USER_NAME,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    logger.info("Seed user created", user_id=str(SEED_USER_ID))
    return user
