import uuid
from sqlalchemy import String, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sentinel_api.database.base import BaseModel


class IncidentMemory(BaseModel):
    """Stores historical context of resolved incidents for AI Memory retrieval."""
    
    __tablename__ = "incident_memories"

    incident_id: Mapped[str] = mapped_column(String, index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    summary: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    time_taken_ms: Mapped[int] = mapped_column(Integer, default=0)
    
    root_cause: Mapped[dict] = mapped_column(JSON, default=dict)
    recommended_fix: Mapped[dict] = mapped_column(JSON, default=dict)
    generated_report: Mapped[dict] = mapped_column(JSON, default=dict)
    timeline: Mapped[list] = mapped_column(JSON, default=list)
    
    logs_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    deployment_summary: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    tags: Mapped[list["IncidentTag"]] = relationship(
        "IncidentTag", back_populates="memory", cascade="all, delete-orphan"
    )
    embedding: Mapped["IncidentEmbedding"] = relationship(
        "IncidentEmbedding", back_populates="memory", uselist=False, cascade="all, delete-orphan"
    )


class IncidentTag(BaseModel):
    """Tags for fast filtering (e.g. environment=prod, service=auth)."""
    
    __tablename__ = "incident_tags"

    memory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incident_memories.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    value: Mapped[str] = mapped_column(String, nullable=True, index=True)

    memory: Mapped["IncidentMemory"] = relationship("IncidentMemory", back_populates="tags")


class IncidentEmbedding(BaseModel):
    """Future-proof table for Vector DB integration or local pgvector."""
    
    __tablename__ = "incident_embeddings"

    memory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incident_memories.id", ondelete="CASCADE"), index=True, unique=True)
    
    # Placeholder for pgvector or reference to external vector store ID
    vector_reference: Mapped[str] = mapped_column(String, nullable=True)
    
    memory: Mapped["IncidentMemory"] = relationship("IncidentMemory", back_populates="embedding")
