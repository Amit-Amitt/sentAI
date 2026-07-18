import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class WorkspaceMember(BaseModel):
    """Junction table associating a User to a Workspace."""

    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "workspace_id", name="uq_workspace_member_user_ws"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    last_active: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("User", lazy="selectin")
    workspace = relationship("Workspace", back_populates="members", lazy="selectin")
