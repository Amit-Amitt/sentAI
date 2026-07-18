"""Models for Sentinel AI Integrations Marketplace."""

import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class IntegrationProvider(BaseModel):
    """Supported integration provider metadata (e.g. GitHub, Slack, Datadog)."""

    __tablename__ = "integration_providers"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    logo: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    overview: Mapped[str] = mapped_column(String(5000), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="available", nullable=False)  # available, coming_soon, beta
    is_oauth_supported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_sync_frequency: Mapped[str] = mapped_column(String(50), default="daily", nullable=False)


class WorkspaceIntegration(BaseModel):
    """Active integration connection settings configured within a workspace."""

    __tablename__ = "workspace_integrations"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("integration_providers.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50), default="disconnected", nullable=False
    )  # available, connected, disconnected, error, syncing, disabled
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    workspace = relationship("Workspace", lazy="selectin")
    provider = relationship("IntegrationProvider", lazy="selectin")

    credentials = relationship(
        "IntegrationCredential",
        back_populates="workspace_integration",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    webhooks = relationship(
        "IntegrationWebhook",
        back_populates="workspace_integration",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    syncs = relationship(
        "IntegrationSync",
        back_populates="workspace_integration",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    audits = relationship(
        "IntegrationAudit",
        back_populates="workspace_integration",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class IntegrationCredential(BaseModel):
    """Secure tokens and keys corresponding to a workspace integration."""

    __tablename__ = "integration_credentials"

    workspace_integration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace_integrations.id", ondelete="CASCADE"),
        nullable=False,
    )
    credential_type: Mapped[str] = mapped_column(String(50), nullable=False)  # api_key, oauth_token, webhook_secret
    key: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. token, api_key, client_secret
    value: Mapped[str] = mapped_column(String(1000), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    workspace_integration = relationship("WorkspaceIntegration", back_populates="credentials")


class IntegrationWebhook(BaseModel):
    """Webhooks connected with the workspace integration for push telemetry updates."""

    __tablename__ = "integration_webhooks"

    workspace_integration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace_integrations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), default="incoming", nullable=False)  # incoming, outgoing
    secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    retry_strategy: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, inactive, error
    delivery_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # success, failed
    delivery_history: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)

    workspace_integration = relationship("WorkspaceIntegration", back_populates="webhooks")


class IntegrationSync(BaseModel):
    """Synchronization telemetry pipeline logs for each workspace integration."""

    __tablename__ = "integration_syncs"

    workspace_integration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace_integrations.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), default="success", nullable=False)  # success, failed, running
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    imported_resources: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)
    warnings: Mapped[List[Any]] = mapped_column(JSON, default=list, nullable=False)

    workspace_integration = relationship("WorkspaceIntegration", back_populates="syncs")


class IntegrationAudit(BaseModel):
    """Audit logs for actions performed on workspace integrations."""

    __tablename__ = "integration_audits"

    workspace_integration_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspace_integrations.id", ondelete="SET NULL"),
        nullable=True,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # connected, disconnected, config_updated, etc.
    performed_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    workspace_integration = relationship("WorkspaceIntegration", back_populates="audits")
    performed_by = relationship("User", lazy="selectin")
