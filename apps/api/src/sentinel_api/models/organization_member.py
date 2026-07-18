import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class OrganizationMember(BaseModel):
    """Junction table associating a User to an Organization with a Role."""

    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "organization_id", name="uq_organization_member_user_org"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", index=True
    )
    last_active: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("User", lazy="selectin")
    organization = relationship(
        "Organization", back_populates="members", lazy="selectin"
    )
    role = relationship("Role", lazy="selectin")
