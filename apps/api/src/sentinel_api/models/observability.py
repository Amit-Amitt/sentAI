import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import String, JSON, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class ObservabilityIntegration(BaseModel):
    """Configuration for external observability stacks (Prometheus, Grafana, Loki, etc.)."""
    __tablename__ = "observability_integrations"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    integration_type: Mapped[str] = mapped_column(String, index=True, nullable=False) # prometheus, grafana, loki, tempo, jaeger, alertmanager
    
    url: Mapped[str] = mapped_column(String, nullable=False)
    
    # Store credentials securely (encrypted in a real implementation)
    auth_method: Mapped[str] = mapped_column(String, default="none", nullable=False) # none, basic, bearer, api_key
    credentials: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False) 
    
    status: Mapped[str] = mapped_column(String, default="active", nullable=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class GrafanaDashboard(BaseModel):
    """Synchronized Grafana Dashboards for quick correlation."""
    __tablename__ = "grafana_dashboards"

    integration_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("observability_integrations.id", ondelete="CASCADE"), index=True, nullable=False)
    
    uid: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    folder_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    tags: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    panels: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)


class PrometheusRule(BaseModel):
    """Synchronized Prometheus recording and alerting rules."""
    __tablename__ = "prometheus_rules"

    integration_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("observability_integrations.id", ondelete="CASCADE"), index=True, nullable=False)
    
    group_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    query: Mapped[str] = mapped_column(String, nullable=False)
    duration: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    labels: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)
    annotations: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)
    
    rule_type: Mapped[str] = mapped_column(String, nullable=False) # alerting, recording


class AlertmanagerSilence(BaseModel):
    """Synchronized Alertmanager Silences to prevent false positive AI incidents."""
    __tablename__ = "alertmanager_silences"

    integration_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("observability_integrations.id", ondelete="CASCADE"), index=True, nullable=False)
    
    silence_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, index=True, nullable=False) # active, expired, pending
    
    matchers: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
