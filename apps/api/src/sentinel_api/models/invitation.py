import uuid
from datetime import datetime
from typing import Any, List

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class Invitation(BaseModel):
    """Pending/completed team invitation to join an organization and optional workspaces."""

    __tablename__ = "invitations"

    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="engineer")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    token: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    workspaces: Mapped[List[str]] = mapped_column(JSON, default=list)

    # Parent organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    organization = relationship(
        "Organization", back_populates="invitations", lazy="selectin"
    )

    # Who sent the invitation
    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
