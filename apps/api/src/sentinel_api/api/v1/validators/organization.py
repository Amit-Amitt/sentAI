"""Request validators for organization endpoints."""

from pydantic import BaseModel, Field


class CreateOrganizationRequest(BaseModel):
    """Payload for creating a new organization."""

    name: str = Field(
        ..., min_length=2, max_length=255, description="Organization display name"
    )
    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL-safe slug (lowercase, hyphens only)",
    )
    industry: str | None = Field(None, max_length=100, description="Industry vertical")
    region: str | None = Field(None, max_length=100, description="Geographic region")
    timezone: str | None = Field("UTC", max_length=50, description="IANA timezone")


class UpdateOrganizationRequest(BaseModel):
    """Payload for updating an existing organization."""

    name: str | None = Field(None, min_length=2, max_length=255)
    logo_url: str | None = Field(None, max_length=2048)
    industry: str | None = Field(None, max_length=100)
    region: str | None = Field(None, max_length=100)
    timezone: str | None = Field(None, max_length=50)
