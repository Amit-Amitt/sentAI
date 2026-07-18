import { axiosInstance } from "../axios";

export interface MemoryTag {
  name: string;
  value: string | null;
}

export interface IncidentMemory {
  id: string;
  incident_id: string;
  summary: string;
  severity: string;
  status: string;
  confidence: number;
  time_taken_ms: number;
  root_cause: any;
  recommended_fix: any;
  generated_report: any;
  timeline: any[];
  tags: MemoryTag[];
}

export const memoryService = {
  listMemories: async (
    workspaceId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<IncidentMemory[]> => {
    const { data } = await axiosInstance.get<IncidentMemory[]>("/memory", {
      params: { workspace_id: workspaceId, limit, offset },
    });
    return data;
  },

  searchSimilar: async (
    workspaceId: string,
    query: string,
    limit: number = 5
  ): Promise<IncidentMemory[]> => {
    const { data } = await axiosInstance.get<IncidentMemory[]>("/memory/search", {
      params: { workspace_id: workspaceId, q: query, limit },
    });
    return data;
  },

  getMemory: async (workspaceId: string, id: string): Promise<IncidentMemory> => {
    const { data } = await axiosInstance.get<IncidentMemory>(`/memory/${id}`, {
      params: { workspace_id: workspaceId },
    });
    return data;
  },
};
