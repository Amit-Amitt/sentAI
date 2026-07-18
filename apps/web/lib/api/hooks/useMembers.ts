import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { organizationsService } from "../services/organizations";
import type {
  AddMemberRequest,
  UpdateMemberRoleRequest,
  CreateInvitationRequest,
} from "../types";

export function useMembers(
  orgId: string | null,
  search?: string,
  roleFilter?: string,
  limit: number = 50,
  offset: number = 0
) {
  return useQuery({
    queryKey: ["members", orgId, search, roleFilter, limit, offset],
    queryFn: () =>
      organizationsService.listMembers(
        orgId!,
        search,
        roleFilter,
        limit,
        offset
      ),
    enabled: !!orgId,
  });
}

export function useAddMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      orgId,
      payload,
    }: {
      orgId: string;
      payload: AddMemberRequest;
    }) => organizationsService.addMember(orgId, payload),
    onSuccess: (_data, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ["members", orgId] });
      queryClient.invalidateQueries({ queryKey: ["activities", orgId] });
    },
  });
}

export function useUpdateMemberRole() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      orgId,
      memberId,
      payload,
    }: {
      orgId: string;
      memberId: string;
      payload: UpdateMemberRoleRequest;
    }) => organizationsService.updateMemberRole(orgId, memberId, payload),
    onSuccess: (_data, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ["members", orgId] });
      queryClient.invalidateQueries({ queryKey: ["activities", orgId] });
    },
  });
}

export function useRemoveMember() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      orgId,
      memberId,
    }: {
      orgId: string;
      memberId: string;
    }) => organizationsService.removeMember(orgId, memberId),
    onSuccess: (_data, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ["members", orgId] });
      queryClient.invalidateQueries({ queryKey: ["activities", orgId] });
    },
  });
}

export function useTransferOwnership() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      orgId,
      memberId,
    }: {
      orgId: string;
      memberId: string;
    }) => organizationsService.transferOwnership(orgId, memberId),
    onSuccess: (_data, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ["members", orgId] });
      queryClient.invalidateQueries({ queryKey: ["activities", orgId] });
    },
  });
}

export function useInvitations(orgId: string | null) {
  return useQuery({
    queryKey: ["invitations", orgId],
    queryFn: () => organizationsService.listInvitations(orgId!),
    enabled: !!orgId,
  });
}

export function useCreateInvitation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      orgId,
      payload,
    }: {
      orgId: string;
      payload: CreateInvitationRequest;
    }) => organizationsService.createInvitation(orgId, payload),
    onSuccess: (_data, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ["invitations", orgId] });
      queryClient.invalidateQueries({ queryKey: ["activities", orgId] });
    },
  });
}

export function useResendInvitation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      orgId,
      invitationId,
    }: {
      orgId: string;
      invitationId: string;
    }) => organizationsService.resendInvitation(orgId, invitationId),
    onSuccess: (_data, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ["invitations", orgId] });
      queryClient.invalidateQueries({ queryKey: ["activities", orgId] });
    },
  });
}

export function useCancelInvitation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      orgId,
      invitationId,
    }: {
      orgId: string;
      invitationId: string;
    }) => organizationsService.cancelInvitation(orgId, invitationId),
    onSuccess: (_data, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ["invitations", orgId] });
      queryClient.invalidateQueries({ queryKey: ["activities", orgId] });
    },
  });
}

export function useInvitation(token: string | null) {
  return useQuery({
    queryKey: ["invitation", token],
    queryFn: () => organizationsService.getInvitation(token!),
    enabled: !!token,
  });
}

export function useAcceptInvitation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (token: string) => organizationsService.acceptInvitation(token),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
      queryClient.invalidateQueries({ queryKey: ["workspaces", data.organization_id] });
    },
  });
}

export function useRejectInvitation() {
  return useMutation({
    mutationFn: (token: string) => organizationsService.rejectInvitation(token),
  });
}

export function useActivities(
  orgId: string | null,
  limit: number = 50,
  offset: number = 0
) {
  return useQuery({
    queryKey: ["activities", orgId, limit, offset],
    queryFn: () => organizationsService.listActivities(orgId!, limit, offset),
    enabled: !!orgId,
  });
}
