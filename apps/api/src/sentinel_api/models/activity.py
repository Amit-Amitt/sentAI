import uuid
from typing import Any, Dict

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class MemberActivity(BaseModel):
    """Audit logs for team and organization collaboration actions."""

    __tablename__ = "member_activities"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    user = relationship("User", lazy="selectin")
    organization = relationship("Organization", lazy="selectin")
