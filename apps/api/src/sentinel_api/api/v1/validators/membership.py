"""Request validators for membership endpoints."""

from pydantic import BaseModel, Field


class AddMemberRequest(BaseModel):
    """Payload for adding a member to an organization."""

    email: str = Field(..., max_length=320, description="Email of the user to add")
    role: str = Field(
        "engineer", description="Role: owner, admin, engineer, viewer"
    )


class UpdateMemberRoleRequest(BaseModel):
    """Payload for updating a member's role."""

    role: str = Field(..., description="New role: owner, admin, engineer, viewer")
