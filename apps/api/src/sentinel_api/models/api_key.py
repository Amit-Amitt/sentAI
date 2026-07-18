"""Models for API Key Management System."""

import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class ApiKey(BaseModel):
    """API Key credentials model."""

    __tablename__ = "api_keys"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    prefix: Mapped[str] = mapped_column(String(50), nullable=False)
    secret_hash: Mapped[str] = mapped_column(
        String(64), index=True, unique=True, nullable=False
    )
    environment: Mapped[str] = mapped_column(String(20), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="active", nullable=False
    )  # active, expired, revoked, disabled

    # Scoped Workspace
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    workspace = relationship("Workspace", lazy="selectin")

    # Created By User
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by = relationship("User", lazy="selectin")

    # Child Relationships
    permissions = relationship(
        "ApiKeyPermission",
        back_populates="api_key",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    usages = relationship(
        "ApiKeyUsage",
        back_populates="api_key",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    audits = relationship(
        "ApiKeyAudit",
        back_populates="api_key",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ApiKeyPermission(BaseModel):
    """Permissions/scopes mapped to an API Key."""

    __tablename__ = "api_key_permissions"

    api_key_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=False,
    )
    scope: Mapped[str] = mapped_column(String(100), nullable=False)

    api_key = relationship("ApiKey", back_populates="permissions")


class ApiKeyUsage(BaseModel):
    """API Key usage tracking records."""

    __tablename__ = "api_key_usages"

    api_key_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=False,
    )
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    api_key = relationship("ApiKey", back_populates="usages")


class ApiKeyAudit(BaseModel):
    """Audit logs tracking modifications/actions performed on API Keys."""

    __tablename__ = "api_key_audits"

    api_key_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # created, copied, rotated, revoked, deleted, scope_changed, expiration_changed
    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    api_key = relationship("ApiKey", back_populates="audits")
    performed_by = relationship("User", lazy="selectin")
