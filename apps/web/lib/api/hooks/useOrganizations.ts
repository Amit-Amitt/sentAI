import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { organizationsService } from "../services/organizations";
import type {
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
} from "../types";

export function useOrganizations() {
  return useQuery({
    queryKey: ["organizations"],
    queryFn: () => organizationsService.listOrganizations(),
  });
}

export function useOrganization(orgId: string | null) {
  return useQuery({
    queryKey: ["organization", orgId],
    queryFn: () => organizationsService.getOrganization(orgId!),
    enabled: !!orgId,
  });
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateOrganizationRequest) =>
      organizationsService.createOrganization(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
}

export function useUpdateOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      orgId,
      payload,
    }: {
      orgId: string;
      payload: UpdateOrganizationRequest;
    }) => organizationsService.updateOrganization(orgId, payload),
    onSuccess: (_data, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
      queryClient.invalidateQueries({ queryKey: ["organization", orgId] });
    },
  });
}

export function useDeleteOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (orgId: string) =>
      organizationsService.deleteOrganization(orgId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
}
