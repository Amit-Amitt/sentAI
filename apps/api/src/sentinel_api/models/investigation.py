import uuid
from typing import Any, Dict
from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_api.database.base import BaseModel


class Investigation(BaseModel):
    """Database model storing historical incident run states and reports."""

    __tablename__ = "investigations"

    incident_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(String, nullable=True)
    agent_outputs: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    incident_report: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
