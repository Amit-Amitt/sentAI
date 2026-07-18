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

  listMembers: async (orgId: string): Promise<MembershipListResponse> => {
    const { data } = await axiosInstance.get<MembershipListResponse>(
      `/organizations/${orgId}/members`
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
};
