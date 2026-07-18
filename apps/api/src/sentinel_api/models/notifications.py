import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import String, JSON, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_api.database.base import BaseModel


class NotificationChannel(BaseModel):
    """Configuration for external notification endpoints (Slack, Teams, etc.)."""
    __tablename__ = "notification_channels"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    provider_type: Mapped[str] = mapped_column(String, index=True, nullable=False) # slack, teams, discord, pagerduty, email, webhook
    
    # Store credentials securely
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class NotificationPolicy(BaseModel):
    """Routing rules mapping incident severity/service to a specific channel."""
    __tablename__ = "notification_policies"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    channel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notification_channels.id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Matching rules (e.g., {"severity": ["High", "Critical"], "service": ["api", "db"]})
    rules: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class EscalationPolicy(BaseModel):
    """Escalation definitions for unacknowledged incidents."""
    __tablename__ = "escalation_policies"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    # e.g. [{"level": 1, "timeout_mins": 15, "channel_id": "...", "target_user_id": "..."}, ...]
    steps: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class OnCallSchedule(BaseModel):
    """Tracks on-call users and overrides."""
    __tablename__ = "oncall_schedules"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    primary_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    secondary_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Overrides e.g. [{"user_id": "...", "start": "...", "end": "..."}]
    overrides: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    timezone: Mapped[str] = mapped_column(String, default="UTC", nullable=False)


class NotificationHistory(BaseModel):
    """Audit log of delivered notifications."""
    __tablename__ = "notification_history"

    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False)
    channel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notification_channels.id", ondelete="CASCADE"), index=True, nullable=False)
    
    status: Mapped[str] = mapped_column(String, nullable=False) # pending, delivered, failed
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class IncidentComment(BaseModel):
    """Collaboration comments on an incident timeline."""
    __tablename__ = "incident_comments"

    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    content: Mapped[str] = mapped_column(String, nullable=False)
    attachments: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    
    # For syncing with Slack threads
    external_message_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class IncidentAcknowledgement(BaseModel):
    """Tracking when and who acknowledged an incident."""
    __tablename__ = "incident_acknowledgements"

    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    action: Mapped[str] = mapped_column(String, nullable=False) # acknowledged, resolved, snoozed
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
