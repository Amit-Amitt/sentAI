import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiKeysService } from "../services/apikeys";
import type { ApiKeyCreatePayload, ApiKeyUpdatePayload } from "../types";

export function useApiKeys(workspaceId: string | null) {
  return useQuery({
    queryKey: ["apikeys", workspaceId],
    queryFn: () => apiKeysService.listApiKeys(workspaceId!),
    enabled: !!workspaceId,
  });
}

export function useApiKey(keyId: string | null) {
  return useQuery({
    queryKey: ["apikey", keyId],
    queryFn: () => apiKeysService.getApiKey(keyId!),
    enabled: !!keyId,
  });
}

export function useApiKeyUsage(keyId: string | null) {
  return useQuery({
    queryKey: ["apikey-usage", keyId],
    queryFn: () => apiKeysService.getApiKeyUsage(keyId!),
    enabled: !!keyId,
    refetchInterval: 10000, // Auto-refetch usage statistics every 10 seconds for live updates
  });
}

export function useApiKeyAudits(keyId: string | null) {
  return useQuery({
    queryKey: ["apikey-audits", keyId],
    queryFn: () => apiKeysService.getApiKeyAudits(keyId!),
    enabled: !!keyId,
  });
}

export function useCreateApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      workspaceId,
      payload,
    }: {
      workspaceId: string;
      payload: ApiKeyCreatePayload;
    }) => apiKeysService.createApiKey(workspaceId, payload),
    onSuccess: (_data, { workspaceId }) => {
      queryClient.invalidateQueries({ queryKey: ["apikeys", workspaceId] });
    },
  });
}

export function useUpdateApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      keyId,
      payload,
    }: {
      keyId: string;
      payload: ApiKeyUpdatePayload;
    }) => apiKeysService.updateApiKey(keyId, payload),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["apikeys", data.workspace_id] });
      queryClient.invalidateQueries({ queryKey: ["apikey", data.id] });
      queryClient.invalidateQueries({ queryKey: ["apikey-usage", data.id] });
    },
  });
}

export function useDeleteApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ keyId }: { keyId: string; workspaceId: string }) =>
      apiKeysService.deleteApiKey(keyId),
    onSuccess: (_data, { workspaceId }) => {
      queryClient.invalidateQueries({ queryKey: ["apikeys", workspaceId] });
    },
  });
}

export function useRotateApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (keyId: string) => apiKeysService.rotateApiKey(keyId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["apikeys", data.workspace_id] });
      queryClient.invalidateQueries({ queryKey: ["apikey", data.id] });
      queryClient.invalidateQueries({ queryKey: ["apikey-usage", data.id] });
    },
  });
}

export function useRevokeApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (keyId: string) => apiKeysService.revokeApiKey(keyId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["apikeys", data.workspace_id] });
      queryClient.invalidateQueries({ queryKey: ["apikey", data.id] });
      queryClient.invalidateQueries({ queryKey: ["apikey-usage", data.id] });
    },
  });
}

export function useCopyApiKey() {
  return useMutation({
    mutationFn: (keyId: string) => apiKeysService.copyApiKey(keyId),
  });
}
