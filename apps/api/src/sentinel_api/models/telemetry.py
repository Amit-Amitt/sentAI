import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import datetime

from sentinel_api.database.base import Base

class TelemetryEvent(Base):
    """
    TelemetryEvent stores logs, metrics, traces, exceptions, and events sent by the Agent SDK.
    """
    __tablename__ = "telemetry_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    payload = Column(JSONB, nullable=False, default=dict)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)

    project = relationship("Project")
    workspace = relationship("Workspace")


class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    message = Column(String, nullable=False)
    metadata_json = Column("metadata", JSONB, nullable=True, default=dict)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)


class TelemetryMetric(Base):
    __tablename__ = "telemetry_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    tags = Column(JSONB, nullable=True, default=dict)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)


class TelemetryException(Base):
    __tablename__ = "telemetry_exceptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(100), nullable=True, index=True)
    message = Column(String, nullable=False)
    stack_trace = Column(String, nullable=True)
    tags = Column(JSONB, nullable=True, default=dict)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)


class TelemetryHeartbeat(Base):
    __tablename__ = "telemetry_heartbeats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    environment = Column(String(50), nullable=False, index=True)
    version = Column(String(50), nullable=True)
    cpu = Column(Float, nullable=True)
    memory = Column(Float, nullable=True)
    health = Column(String(20), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)


class TelemetryDeployment(Base):
    __tablename__ = "telemetry_deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(String(50), nullable=False, index=True)
    environment = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    metadata_json = Column("metadata", JSONB, nullable=True, default=dict)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)


class TelemetryHealth(Base):
    __tablename__ = "telemetry_health"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    service_name = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    latency_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)
