import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { organizationsService } from "../services/organizations";
import type {
  AddMemberRequest,
  UpdateMemberRoleRequest,
  CreateInvitationRequest,
} from "../types";

export function useMembers(orgId: string | null) {
  return useQuery({
    queryKey: ["members", orgId],
    queryFn: () => organizationsService.listMembers(orgId!),
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
    },
  });
}
