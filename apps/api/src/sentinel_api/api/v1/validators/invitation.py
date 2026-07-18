"""Request validators for invitation endpoints."""

from pydantic import BaseModel, Field


class CreateInvitationRequest(BaseModel):
    """Payload for inviting a user to an organization."""

    email: str = Field(..., max_length=320, description="Email to invite")
    role: str = Field(
        "engineer", description="Role to assign: admin, engineer, viewer"
    )
