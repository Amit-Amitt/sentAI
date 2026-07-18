import { axiosInstance } from "../axios";
import {
  IncidentAnalyzeRequest,
  AnalysisSubmitResponse,
  InvestigationListResponse,
  IncidentReport,
} from "../types";

export const incidentsService = {
  listIncidents: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<InvestigationListResponse> => {
    const { data } = await axiosInstance.get<InvestigationListResponse>("/incidents", {
      params: {
        skip: params?.skip ?? 0,
        limit: params?.limit ?? 100,
        status: params?.status === "ALL" ? undefined : params?.status,
        sort_by: params?.sort_by ?? "created_at",
        sort_order: params?.sort_order ?? "desc",
      },
    });
    return data;
  },

  getIncident: async (incidentId: string): Promise<IncidentReport> => {
    const { data } = await axiosInstance.get<IncidentReport>(`/incidents/${incidentId}`);
    return data;
  },

  analyzeIncident: async (payload: IncidentAnalyzeRequest): Promise<AnalysisSubmitResponse> => {
    const { data } = await axiosInstance.post<AnalysisSubmitResponse>("/incidents/analyze", payload);
    return data;
  },

  deleteIncident: async (incidentId: string): Promise<{ success: boolean; message: string }> => {
    const { data } = await axiosInstance.delete<{ success: boolean; message: string }>(
      `/incidents/${incidentId}`
    );
    return data;
  },
};
