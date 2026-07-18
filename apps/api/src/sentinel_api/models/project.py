import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from sentinel_api.database.base import Base

class Project(Base):
    """
    Project represents a connected application that reports telemetry to Sentinel AI.
    """
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    environment = Column(String(50), nullable=False, default="production")
    language = Column(String(50), nullable=True)
    framework = Column(String(50), nullable=True)
    api_key = Column(String(128), nullable=False, unique=True, index=True)
    status = Column(String(50), nullable=False, default="ACTIVE")

    workspace = relationship("Workspace")
