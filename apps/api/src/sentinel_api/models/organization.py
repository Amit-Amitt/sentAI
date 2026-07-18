"""Organization model — top-level tenant entity."""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class Organization(BaseModel):
    """Organization representing a company or team tenant."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default="UTC"
    )

    # Owner relationship
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    owner = relationship("User", back_populates="owned_organizations", lazy="selectin")

    # Children
    workspaces = relationship(
        "Workspace",
        back_populates="organization",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    memberships = relationship(
        "Membership",
        back_populates="organization",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    invitations = relationship(
        "Invitation",
        back_populates="organization",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
