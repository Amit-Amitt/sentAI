"""Repository for User entity database operations."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.user import User


class UserRepository:
    """Data access layer for User entities."""

    async def create(
        self,
        db: AsyncSession,
        email: str,
        full_name: str,
        avatar_url: Optional[str] = None,
    ) -> User:
        """Creates a new user record."""
        db_obj = User(email=email, full_name=full_name, avatar_url=avatar_url)
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Retrieves a user by primary key."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Retrieves a user by email address."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def update(
        self,
        db: AsyncSession,
        user: User,
        **kwargs: object,
    ) -> User:
        """Updates user fields."""
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        await db.flush()
        return user
