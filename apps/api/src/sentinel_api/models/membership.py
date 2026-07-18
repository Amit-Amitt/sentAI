"""Membership model — links users to organizations with roles."""

import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class Membership(BaseModel):
    """Junction entity associating a user with an organization and optional workspace scope."""

    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "organization_id",
            "workspace_id",
            name="uq_membership_user_org_ws",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="viewer")

    # Relationships
    user = relationship("User", back_populates="memberships", lazy="selectin")
    organization = relationship(
        "Organization", back_populates="memberships", lazy="selectin"
    )
