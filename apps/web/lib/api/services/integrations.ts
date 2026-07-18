import { axiosInstance } from "../axios";
import type {
  IntegrationProvider,
  WorkspaceConnection,
  ConnectIntegrationPayload,
  UpdateIntegrationPayload,
  ConnectionTestResponse,
  SyncTriggerResponse,
  IntegrationHistoryResponse,
} from "../types";

export const integrationsService = {
  listProviders: async (
    workspaceId?: string | null
  ): Promise<IntegrationProvider[]> => {
    const params = workspaceId ? `?workspace_id=${workspaceId}` : "";
    const { data } = await axiosInstance.get<IntegrationProvider[]>(
      `/integrations${params}`
    );
    return data;
  },

  getProvider: async (
    providerId: string,
    workspaceId?: string | null
  ): Promise<IntegrationProvider> => {
    const params = workspaceId ? `?workspace_id=${workspaceId}` : "";
    const { data } = await axiosInstance.get<IntegrationProvider>(
      `/integrations/${providerId}${params}`
    );
    return data;
  },

  connectIntegration: async (
    workspaceId: string,
    payload: ConnectIntegrationPayload
  ): Promise<WorkspaceConnection> => {
    const { data } = await axiosInstance.post<WorkspaceConnection>(
      `/integrations?workspace_id=${workspaceId}`,
      payload
    );
    return data;
  },

  updateIntegration: async (
    connectionId: string,
    workspaceId: string,
    payload: UpdateIntegrationPayload
  ): Promise<WorkspaceConnection> => {
    const { data } = await axiosInstance.patch<WorkspaceConnection>(
      `/integrations/${connectionId}?workspace_id=${workspaceId}`,
      payload
    );
    return data;
  },

  disconnectIntegration: async (
    connectionId: string,
    workspaceId: string
  ): Promise<WorkspaceConnection> => {
    const { data } = await axiosInstance.post<WorkspaceConnection>(
      `/integrations/${connectionId}/disconnect?workspace_id=${workspaceId}`
    );
    return data;
  },

  deleteIntegration: async (
    connectionId: string,
    workspaceId: string
  ): Promise<{ success: boolean }> => {
    const { data } = await axiosInstance.delete<{ success: boolean }>(
      `/integrations/${connectionId}?workspace_id=${workspaceId}`
    );
    return data;
  },

  testConnection: async (
    connectionId: string,
    workspaceId: string
  ): Promise<ConnectionTestResponse> => {
    const { data } = await axiosInstance.post<ConnectionTestResponse>(
      `/integrations/${connectionId}/test?workspace_id=${workspaceId}`
    );
    return data;
  },

  triggerSync: async (
    connectionId: string,
    workspaceId: string
  ): Promise<SyncTriggerResponse> => {
    const { data } = await axiosInstance.post<SyncTriggerResponse>(
      `/integrations/${connectionId}/sync?workspace_id=${workspaceId}`
    );
    return data;
  },

  getHistory: async (
    connectionId: string,
    workspaceId: string
  ): Promise<IntegrationHistoryResponse> => {
    const { data } = await axiosInstance.get<IntegrationHistoryResponse>(
      `/integrations/${connectionId}/history?workspace_id=${workspaceId}`
    );
    return data;
  },
};
