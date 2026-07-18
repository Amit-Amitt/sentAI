"""Request validators for workspace endpoints."""

from typing import Any, Dict

from pydantic import BaseModel, Field


class CreateWorkspaceRequest(BaseModel):
    """Payload for creating a new workspace within an organization."""

    name: str = Field(
        ..., min_length=2, max_length=255, description="Workspace display name"
    )
    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL-safe slug (lowercase, hyphens only)",
    )
    environment: str = Field(
        "development",
        description="Environment type: development, staging, production",
    )
    description: str | None = Field(
        None, max_length=1000, description="Workspace description"
    )


class UpdateWorkspaceRequest(BaseModel):
    """Payload for updating workspace settings."""

    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    environment: str | None = Field(None)
    ai_config: Dict[str, Any] | None = Field(None)
    incident_retention_days: int | None = Field(None, ge=1, le=3650)
