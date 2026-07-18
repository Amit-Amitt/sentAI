"""API routes for organization, membership, and invitation endpoints."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.api.v1.controllers.organizations import OrganizationsController
from sentinel_api.api.v1.dependencies.current_user import get_current_user
from sentinel_api.api.v1.dependencies.services import (
    get_invitation_service,
    get_membership_service,
    get_organization_service,
)
from sentinel_api.api.v1.responses.organization import (
    InvitationListResponse,
    InvitationResponse,
    MembershipListResponse,
    MembershipResponse,
    OrganizationListResponse,
    OrganizationResponse,
)
from sentinel_api.api.v1.responses.schemas import DeleteResponse
from sentinel_api.api.v1.validators.invitation import CreateInvitationRequest
from sentinel_api.api.v1.validators.membership import (
    AddMemberRequest,
    UpdateMemberRoleRequest,
)
from sentinel_api.api.v1.validators.organization import (
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
)
from sentinel_api.database.session import get_db_session
from sentinel_api.models.user import User
from sentinel_api.services.invitation import InvitationService
from sentinel_api.services.membership import MembershipService
from sentinel_api.services.organization import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


def get_controller(
    org_service: OrganizationService = Depends(get_organization_service),
    membership_service: MembershipService = Depends(get_membership_service),
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> OrganizationsController:
    return OrganizationsController(org_service, membership_service, invitation_service)


# ── Organization CRUD ──────────────────────────────────────────


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    payload: CreateOrganizationRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    controller: OrganizationsController = Depends(get_controller),
) -> OrganizationResponse:
    """Creates a new organization with the current user as owner."""
    return await controller.create(db, payload, user.id)


@router.get("", response_model=OrganizationListResponse)
async def list_organizations(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    controller: OrganizationsController = Depends(get_controller),
) -> OrganizationListResponse:
    """Lists all organizations the current user belongs to."""
    return await controller.list_all(db, user.id)


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: OrganizationsController = Depends(get_controller),
) -> OrganizationResponse:
    """Returns details of a specific organization."""
    return await controller.get(db, org_id)


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: uuid.UUID,
    payload: UpdateOrganizationRequest,
    db: AsyncSession = Depends(get_db_session),
    controller: OrganizationsController = Depends(get_controller),
) -> OrganizationResponse:
    """Updates organization profile fields."""
    return await controller.update(db, org_id, payload)


@router.delete("/{org_id}", response_model=DeleteResponse)
async def delete_organization(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: OrganizationsController = Depends(get_controller),
) -> DeleteResponse:
    """Deletes an organization and all its resources."""
    res = await controller.delete(db, org_id)
    return DeleteResponse(success=res["success"], message=res["message"])


# ── Members ────────────────────────────────────────────────────


@router.get("/{org_id}/members", response_model=MembershipListResponse)
async def list_members(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: OrganizationsController = Depends(get_controller),
) -> MembershipListResponse:
    """Lists all members of an organization."""
    return await controller.list_members(db, org_id)


@router.post(
    "/{org_id}/members", response_model=MembershipResponse, status_code=201
)
async def add_member(
    org_id: uuid.UUID,
    payload: AddMemberRequest,
    db: AsyncSession = Depends(get_db_session),
    controller: OrganizationsController = Depends(get_controller),
) -> MembershipResponse:
    """Adds a user to the organization by email."""
    return await controller.add_member(db, org_id, payload)


@router.patch(
    "/{org_id}/members/{member_id}", response_model=MembershipResponse
)
async def update_member_role(
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    payload: UpdateMemberRoleRequest,
    db: AsyncSession = Depends(get_db_session),
    controller: OrganizationsController = Depends(get_controller),
) -> MembershipResponse:
    """Updates the role of a member."""
    return await controller.update_member_role(db, member_id, payload)


@router.delete("/{org_id}/members/{member_id}", response_model=DeleteResponse)
async def remove_member(
    org_id: uuid.UUID,
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: OrganizationsController = Depends(get_controller),
) -> DeleteResponse:
    """Removes a member from the organization."""
    res = await controller.remove_member(db, member_id)
    return DeleteResponse(success=res["success"], message=res["message"])


# ── Invitations ────────────────────────────────────────────────


@router.get("/{org_id}/invitations", response_model=InvitationListResponse)
async def list_invitations(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    controller: OrganizationsController = Depends(get_controller),
) -> InvitationListResponse:
    """Lists all invitations for an organization."""
    return await controller.list_invitations(db, org_id)


@router.post(
    "/{org_id}/invitations", response_model=InvitationResponse, status_code=201
)
async def create_invitation(
    org_id: uuid.UUID,
    payload: CreateInvitationRequest,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
    controller: OrganizationsController = Depends(get_controller),
) -> InvitationResponse:
    """Creates a new invitation to join the organization."""
    return await controller.create_invitation(db, org_id, payload, user.id)
