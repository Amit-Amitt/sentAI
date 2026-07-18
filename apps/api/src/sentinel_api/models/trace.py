import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import String, JSON, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class Trace(BaseModel):
    """Top-level representation of an OpenTelemetry trace."""
    __tablename__ = "traces"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False)
    
    trace_id: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    root_span_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    has_errors: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    spans: Mapped[List["Span"]] = relationship("Span", back_populates="trace", cascade="all, delete-orphan")


class Span(BaseModel):
    """An individual operation within a trace (OpenTelemetry Span)."""
    __tablename__ = "spans"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    trace_id: Mapped[str] = mapped_column(String, ForeignKey("traces.trace_id", ondelete="CASCADE"), index=True, nullable=False)
    
    span_id: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    parent_span_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False) # INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False)
    
    status_code: Mapped[str] = mapped_column(String, nullable=False, default="UNSET") # UNSET, OK, ERROR
    status_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    span_attributes: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    resource_attributes: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    trace: Mapped["Trace"] = relationship("Trace", back_populates="spans")
    events: Mapped[List["SpanEvent"]] = relationship("SpanEvent", back_populates="span", cascade="all, delete-orphan")
    links: Mapped[List["SpanLink"]] = relationship("SpanLink", back_populates="span", cascade="all, delete-orphan")


class SpanEvent(BaseModel):
    """An event occurring during a span (OpenTelemetry SpanEvent)."""
    __tablename__ = "span_events"

    span_id: Mapped[str] = mapped_column(String, ForeignKey("spans.span_id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    attributes: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    span: Mapped["Span"] = relationship("Span", back_populates="events")


class SpanLink(BaseModel):
    """A causal relationship between spans across different traces (OpenTelemetry SpanLink)."""
    __tablename__ = "span_links"

    span_id: Mapped[str] = mapped_column(String, ForeignKey("spans.span_id", ondelete="CASCADE"), index=True, nullable=False)
    
    linked_trace_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    linked_span_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    attributes: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    span: Mapped["Span"] = relationship("Span", back_populates="links")
