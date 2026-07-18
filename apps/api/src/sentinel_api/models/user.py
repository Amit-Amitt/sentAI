"""User model — identity entity for multi-tenant ownership."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class User(BaseModel):
    """Platform user entity. Auth fields (password) deferred to auth implementation."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(320), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    memberships = relationship("Membership", back_populates="user", lazy="selectin")
    owned_organizations = relationship(
        "Organization", back_populates="owner", lazy="selectin"
    )
