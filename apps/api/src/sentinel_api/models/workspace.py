"""Workspace model — isolated environment within an organization."""

import uuid
from typing import Any, Dict

from sqlalchemy import ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class Workspace(BaseModel):
    """Workspace scoping all resources (incidents, reports, etc.) within an org."""

    __tablename__ = "workspaces"
    __table_args__ = (
        UniqueConstraint("organization_id", "slug", name="uq_workspace_org_slug"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    environment: Mapped[str] = mapped_column(
        String(20), nullable=False, default="development"
    )
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ai_config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    incident_retention_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=90
    )

    # Parent organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    organization = relationship(
        "Organization", back_populates="workspaces", lazy="selectin"
    )
