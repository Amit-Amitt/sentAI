"""User model — identity entity for multi-tenant ownership."""

from sqlalchemy import Boolean, String, JSON
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

    # Auth & IAM fields
    hashed_password: Mapped[str | None] = mapped_column(String, nullable=True)
    auth_provider: Mapped[str] = mapped_column(String, default="local", nullable=False) # local, github, google, microsoft, saml
    
    # MFA fields
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String, nullable=True)
    mfa_backup_codes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Relationships
    memberships = relationship("OrganizationMember", back_populates="user", lazy="selectin")
    owned_organizations = relationship(
        "Organization", back_populates="owner", lazy="selectin"
    )
