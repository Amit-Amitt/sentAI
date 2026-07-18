import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workspacesService } from "../services/workspaces";
import type { CreateWorkspaceRequest, UpdateWorkspaceRequest } from "../types";

export function useWorkspaces(orgId: string | null) {
  return useQuery({
    queryKey: ["workspaces", orgId],
    queryFn: () => workspacesService.listWorkspaces(orgId!),
    enabled: !!orgId,
  });
}

export function useWorkspace(wsId: string | null) {
  return useQuery({
    queryKey: ["workspace", wsId],
    queryFn: () => workspacesService.getWorkspace(wsId!),
    enabled: !!wsId,
  });
}

export function useCreateWorkspace() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      orgId,
      payload,
    }: {
      orgId: string;
      payload: CreateWorkspaceRequest;
    }) => workspacesService.createWorkspace(orgId, payload),
    onSuccess: (_data, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: ["workspaces", orgId] });
    },
  });
}

export function useUpdateWorkspace() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      wsId,
      payload,
    }: {
      wsId: string;
      payload: UpdateWorkspaceRequest;
    }) => workspacesService.updateWorkspace(wsId, payload),
    onSuccess: (_data, { wsId }) => {
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
      queryClient.invalidateQueries({ queryKey: ["workspace", wsId] });
    },
  });
}

export function useDeleteWorkspace() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (wsId: string) => workspacesService.deleteWorkspace(wsId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    },
  });
}
