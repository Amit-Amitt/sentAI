import { axiosInstance } from "../axios";

export const agentsService = {
  runAgent: async (
    agentName: string,
    payload: {
      incident_context: Record<string, any>;
      execution_context: Record<string, any>;
      inputs?: Record<string, any>;
    }
  ): Promise<Record<string, any>> => {
    const { data } = await axiosInstance.post<Record<string, any>>(`/agents/${agentName}`, payload);
    return data;
  },
};
