import { axiosInstance } from "../axios";
import type {
  Organization,
  OrganizationListResponse,
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
  Membership,
  MembershipListResponse,
  AddMemberRequest,
  UpdateMemberRoleRequest,
  Invitation,
  InvitationListResponse,
  CreateInvitationRequest,
  MemberActivityListResponse,
} from "../types";

export const organizationsService = {
  // ── Organization CRUD ──────────────────────────────────────

  createOrganization: async (
    payload: CreateOrganizationRequest
  ): Promise<Organization> => {
    const { data } = await axiosInstance.post<Organization>(
      "/organizations",
      payload
    );
    return data;
  },

  listOrganizations: async (): Promise<OrganizationListResponse> => {
    const { data } =
      await axiosInstance.get<OrganizationListResponse>("/organizations");
    return data;
  },

  getOrganization: async (orgId: string): Promise<Organization> => {
    const { data } = await axiosInstance.get<Organization>(
      `/organizations/${orgId}`
    );
    return data;
  },

  updateOrganization: async (
    orgId: string,
    payload: UpdateOrganizationRequest
  ): Promise<Organization> => {
    const { data } = await axiosInstance.patch<Organization>(
      `/organizations/${orgId}`,
      payload
    );
    return data;
  },

  deleteOrganization: async (
    orgId: string
  ): Promise<{ success: boolean; message: string }> => {
    const { data } = await axiosInstance.delete<{
      success: boolean;
      message: string;
    }>(`/organizations/${orgId}`);
    return data;
  },

  // ── Members ────────────────────────────────────────────────

  listMembers: async (
    orgId: string,
    search?: string,
    roleFilter?: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<MembershipListResponse> => {
    const params: Record<string, any> = { limit, offset };
    if (search) params.search = search;
    if (roleFilter && roleFilter !== "all") params.role_filter = roleFilter;

    const { data } = await axiosInstance.get<MembershipListResponse>(
      `/organizations/${orgId}/members`,
      { params }
    );
    return data;
  },

  addMember: async (
    orgId: string,
    payload: AddMemberRequest
  ): Promise<Membership> => {
    const { data } = await axiosInstance.post<Membership>(
      `/organizations/${orgId}/members`,
      payload
    );
    return data;
  },

  updateMemberRole: async (
    orgId: string,
    memberId: string,
    payload: UpdateMemberRoleRequest
  ): Promise<Membership> => {
    const { data } = await axiosInstance.patch<Membership>(
      `/organizations/${orgId}/members/${memberId}`,
      payload
    );
    return data;
  },

  removeMember: async (
    orgId: string,
    memberId: string
  ): Promise<{ success: boolean; message: string }> => {
    const { data } = await axiosInstance.delete<{
      success: boolean;
      message: string;
    }>(`/organizations/${orgId}/members/${memberId}`);
    return data;
  },

  transferOwnership: async (
    orgId: string,
    memberId: string
  ): Promise<Membership> => {
    const { data } = await axiosInstance.post<Membership>(
      `/organizations/${orgId}/members/${memberId}/transfer-ownership`
    );
    return data;
  },

  // ── Invitations ────────────────────────────────────────────

  listInvitations: async (orgId: string): Promise<InvitationListResponse> => {
    const { data } = await axiosInstance.get<InvitationListResponse>(
      `/organizations/${orgId}/invitations`
    );
    return data;
  },

  createInvitation: async (
    orgId: string,
    payload: CreateInvitationRequest
  ): Promise<Invitation> => {
    const { data } = await axiosInstance.post<Invitation>(
      `/organizations/${orgId}/invitations`,
      payload
    );
    return data;
  },

  resendInvitation: async (
    orgId: string,
    invitationId: string
  ): Promise<Invitation> => {
    const { data } = await axiosInstance.post<Invitation>(
      `/organizations/${orgId}/invitations/${invitationId}/resend`
    );
    return data;
  },

  cancelInvitation: async (
    orgId: string,
    invitationId: string
  ): Promise<Invitation> => {
    const { data } = await axiosInstance.delete<Invitation>(
      `/organizations/${orgId}/invitations/${invitationId}`
    );
    return data;
  },

  // ── Public token invitation flows ─────────────────────────

  getInvitation: async (token: string): Promise<Invitation> => {
    const { data } = await axiosInstance.get<Invitation>(
      `/invitations/${token}`
    );
    return data;
  },

  acceptInvitation: async (token: string): Promise<Invitation> => {
    const { data } = await axiosInstance.post<Invitation>(
      `/invitations/${token}/accept`
    );
    return data;
  },

  rejectInvitation: async (token: string): Promise<Invitation> => {
    const { data } = await axiosInstance.post<Invitation>(
      `/invitations/${token}/reject`
    );
    return data;
  },

  // ── Member Audit Activities ────────────────────────────────

  listActivities: async (
    orgId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<MemberActivityListResponse> => {
    const { data } = await axiosInstance.get<MemberActivityListResponse>(
      `/organizations/${orgId}/activity`,
      { params: { limit, offset } }
    );
    return data;
  },
};
