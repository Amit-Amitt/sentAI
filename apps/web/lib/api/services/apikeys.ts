import { axiosInstance } from "../axios";
import type {
  ApiKey,
  ApiKeyCreatePayload,
  ApiKeyUpdatePayload,
  ApiKeyCreatedResponse,
  ApiKeyActionResponse,
  ApiKeyUsageStats,
  ApiKeyAuditListResponse,
  ApiKeysListResponse,
} from "../types";

export const apiKeysService = {
  createApiKey: async (
    workspaceId: string,
    payload: ApiKeyCreatePayload
  ): Promise<ApiKeyCreatedResponse> => {
    const { data } = await axiosInstance.post<ApiKeyCreatedResponse>(
      `/apikeys?workspace_id=${workspaceId}`,
      payload
    );
    return data;
  },

  listApiKeys: async (workspaceId: string): Promise<ApiKeysListResponse> => {
    const { data } = await axiosInstance.get<ApiKeysListResponse>(
      `/apikeys?workspace_id=${workspaceId}`
    );
    return data;
  },

  getApiKey: async (keyId: string): Promise<ApiKey> => {
    const { data } = await axiosInstance.get<ApiKey>(`/apikeys/${keyId}`);
    return data;
  },

  copyApiKey: async (keyId: string): Promise<ApiKeyActionResponse> => {
    const { data } = await axiosInstance.post<ApiKeyActionResponse>(`/apikeys/${keyId}/copy`);
    return data;
  },

  updateApiKey: async (
    keyId: string,
    payload: ApiKeyUpdatePayload
  ): Promise<ApiKey> => {
    const { data } = await axiosInstance.patch<ApiKey>(
      `/apikeys/${keyId}`,
      payload
    );
    return data;
  },

  deleteApiKey: async (
    keyId: string
  ): Promise<{ success: boolean; message: string }> => {
    const { data } = await axiosInstance.delete<{
      success: boolean;
      message: string;
    }>(`/apikeys/${keyId}`);
    return data;
  },

  rotateApiKey: async (keyId: string): Promise<ApiKeyCreatedResponse> => {
    const { data } = await axiosInstance.post<ApiKeyCreatedResponse>(
      `/apikeys/${keyId}/rotate`
    );
    return data;
  },

  revokeApiKey: async (keyId: string): Promise<ApiKey> => {
    const { data } = await axiosInstance.post<ApiKey>(`/apikeys/${keyId}/revoke`);
    return data;
  },

  getApiKeyUsage: async (keyId: string): Promise<ApiKeyUsageStats> => {
    const { data } = await axiosInstance.get<ApiKeyUsageStats>(
      `/apikeys/${keyId}/usage`
    );
    return data;
  },

  getApiKeyAudits: async (keyId: string): Promise<ApiKeyAuditListResponse> => {
    const { data } = await axiosInstance.get<ApiKeyAuditListResponse>(
      `/apikeys/${keyId}/audits`
    );
    return data;
  },
};
