import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { integrationsService } from "../services/integrations";
import type {
  IntegrationProvider,
  ConnectIntegrationPayload,
  UpdateIntegrationPayload,
  ConnectionTestResponse,
  SyncTriggerResponse,
  IntegrationHistoryResponse,
} from "../types";

const INTEGRATIONS_KEY = "integrations";

/** Lists all available integration providers with optional workspace connection overlay. */
export function useIntegrations(workspaceId: string | null | undefined) {
  return useQuery<IntegrationProvider[]>({
    queryKey: [INTEGRATIONS_KEY, "list", workspaceId],
    queryFn: () => integrationsService.listProviders(workspaceId),
    enabled: true,
    staleTime: 60_000,
  });
}

/** Fetches a single integration provider with active connection info. */
export function useIntegration(
  providerId: string | null | undefined,
  workspaceId: string | null | undefined
) {
  return useQuery<IntegrationProvider>({
    queryKey: [INTEGRATIONS_KEY, "detail", providerId, workspaceId],
    queryFn: () => integrationsService.getProvider(providerId!, workspaceId),
    enabled: !!providerId,
    staleTime: 30_000,
  });
}

/** Connects an integration provider to a workspace. */
export function useConnectIntegration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      workspaceId,
      payload,
    }: {
      workspaceId: string;
      payload: ConnectIntegrationPayload;
    }) => integrationsService.connectIntegration(workspaceId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INTEGRATIONS_KEY] });
    },
  });
}

/** Updates an existing workspace integration. */
export function useUpdateIntegration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      connectionId,
      workspaceId,
      payload,
    }: {
      connectionId: string;
      workspaceId: string;
      payload: UpdateIntegrationPayload;
    }) =>
      integrationsService.updateIntegration(connectionId, workspaceId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INTEGRATIONS_KEY] });
    },
  });
}

/** Disconnects an active workspace integration. */
export function useDisconnectIntegration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      connectionId,
      workspaceId,
    }: {
      connectionId: string;
      workspaceId: string;
    }) => integrationsService.disconnectIntegration(connectionId, workspaceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INTEGRATIONS_KEY] });
    },
  });
}

/** Permanently deletes a workspace integration. */
export function useDeleteIntegration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      connectionId,
      workspaceId,
    }: {
      connectionId: string;
      workspaceId: string;
    }) => integrationsService.deleteIntegration(connectionId, workspaceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INTEGRATIONS_KEY] });
    },
  });
}

/** Tests a live connection against the remote system. */
export function useTestConnection() {
  return useMutation<
    ConnectionTestResponse,
    Error,
    { connectionId: string; workspaceId: string }
  >({
    mutationFn: ({ connectionId, workspaceId }) =>
      integrationsService.testConnection(connectionId, workspaceId),
  });
}

/** Triggers a manual synchronization pipeline. */
export function useTriggerSync() {
  const queryClient = useQueryClient();
  return useMutation<
    SyncTriggerResponse,
    Error,
    { connectionId: string; workspaceId: string }
  >({
    mutationFn: ({ connectionId, workspaceId }) =>
      integrationsService.triggerSync(connectionId, workspaceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INTEGRATIONS_KEY] });
    },
  });
}

/** Fetches sync and audit history for a connection. */
export function useIntegrationHistory(
  connectionId: string | null | undefined,
  workspaceId: string | null | undefined
) {
  return useQuery<IntegrationHistoryResponse>({
    queryKey: [INTEGRATIONS_KEY, "history", connectionId, workspaceId],
    queryFn: () =>
      integrationsService.getHistory(connectionId!, workspaceId!),
    enabled: !!connectionId && !!workspaceId,
    staleTime: 15_000,
  });
}
