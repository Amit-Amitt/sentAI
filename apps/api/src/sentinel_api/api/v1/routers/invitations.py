"""API routes for token-based invitation acceptance and rejection."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.dependencies.current_user import get_current_user
from sentinel_api.api.v1.dependencies.services import get_invitation_service
from sentinel_api.api.v1.responses.organization import InvitationResponse
from sentinel_api.database.session import get_db_session
from sentinel_api.models.user import User
from sentinel_api.services.invitation import InvitationService

router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.get("/{token}", response_model=InvitationResponse)
async def get_invitation_details(
    token: str,
    db: AsyncSession = Depends(get_db_session),
    inv_service: InvitationService = Depends(get_invitation_service),
) -> InvitationResponse:
    """Retrieves invitation information using its unique token (public endpoint)."""
    invitation = await inv_service.get_by_token(db, token)
    return InvitationResponse(
        id=str(invitation.id),
        email=invitation.email,
        role=invitation.role,
        status=invitation.status,
        organization_id=str(invitation.organization_id),
        invited_by=str(invitation.invited_by),
        expires_at=invitation.expires_at.isoformat() if invitation.expires_at else None,
        created_at=invitation.created_at.isoformat() if invitation.created_at else None,
        workspaces=invitation.workspaces or [],
    )


@router.post("/{token}/accept", response_model=InvitationResponse)
async def accept_invitation(
    token: str,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    inv_service: InvitationService = Depends(get_invitation_service),
) -> InvitationResponse:
    """Accepts the invitation using token, adding current user to organization and workspaces."""
    invitation = await inv_service.accept_invitation(db, token, user.id)
    return InvitationResponse(
        id=str(invitation.id),
        email=invitation.email,
        role=invitation.role,
        status=invitation.status,
        organization_id=str(invitation.organization_id),
        invited_by=str(invitation.invited_by),
        expires_at=invitation.expires_at.isoformat() if invitation.expires_at else None,
        created_at=invitation.created_at.isoformat() if invitation.created_at else None,
        workspaces=invitation.workspaces or [],
    )


@router.post("/{token}/reject", response_model=InvitationResponse)
async def reject_invitation(
    token: str,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    inv_service: InvitationService = Depends(get_invitation_service),
) -> InvitationResponse:
    """Rejects the invitation using token."""
    invitation = await inv_service.reject_invitation(db, token, user.id)
    return InvitationResponse(
        id=str(invitation.id),
        email=invitation.email,
        role=invitation.role,
        status=invitation.status,
        organization_id=str(invitation.organization_id),
        invited_by=str(invitation.invited_by),
        expires_at=invitation.expires_at.isoformat() if invitation.expires_at else None,
        created_at=invitation.created_at.isoformat() if invitation.created_at else None,
        workspaces=invitation.workspaces or [],
    )
