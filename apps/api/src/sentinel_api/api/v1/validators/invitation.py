"""Request validators for invitation endpoints."""

from typing import List, Optional
from pydantic import BaseModel, Field


class CreateInvitationRequest(BaseModel):
    """Payload for inviting a user to an organization."""

    email: str = Field(..., max_length=320, description="Email to invite")
    role: str = Field(
        "engineer", description="Role to assign: owner, admin, engineer, viewer"
    )
    workspaces: Optional[List[str]] = Field(
        default=None, description="Optional list of workspace IDs to grant access to"
    )
