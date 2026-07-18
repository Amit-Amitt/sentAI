from typing import Optional
import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel

class SimulationRun(BaseModel):
    """Tracks historical simulation triggers and their resulting synthetic investigations."""

    __tablename__ = "simulation_runs"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scenario_id: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="RUNNING", nullable=False)
    
    # We store the synthetic incident_id (string) to link with the investigation record
    incident_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Relationships
    workspace = relationship("Workspace")
