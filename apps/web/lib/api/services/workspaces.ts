import { axiosInstance } from "../axios";
import type {
  Workspace,
  WorkspaceListResponse,
  CreateWorkspaceRequest,
  UpdateWorkspaceRequest,
} from "../types";

export const workspacesService = {
  createWorkspace: async (
    orgId: string,
    payload: CreateWorkspaceRequest
  ): Promise<Workspace> => {
    const { data } = await axiosInstance.post<Workspace>(
      `/organizations/${orgId}/workspaces`,
      payload
    );
    return data;
  },

  listWorkspaces: async (orgId: string): Promise<WorkspaceListResponse> => {
    const { data } = await axiosInstance.get<WorkspaceListResponse>(
      `/organizations/${orgId}/workspaces`
    );
    return data;
  },

  getWorkspace: async (wsId: string): Promise<Workspace> => {
    const { data } = await axiosInstance.get<Workspace>(`/workspaces/${wsId}`);
    return data;
  },

  updateWorkspace: async (
    wsId: string,
    payload: UpdateWorkspaceRequest
  ): Promise<Workspace> => {
    const { data } = await axiosInstance.patch<Workspace>(
      `/workspaces/${wsId}`,
      payload
    );
    return data;
  },

  deleteWorkspace: async (
    wsId: string
  ): Promise<{ success: boolean; message: string }> => {
    const { data } = await axiosInstance.delete<{
      success: boolean;
      message: string;
    }>(`/workspaces/${wsId}`);
    return data;
  },
};
