import { axiosInstance } from "../axios";

export const coordinatorService = {
  run: async (payload: {
    incident_context: Record<string, any>;
    execution_context: Record<string, any>;
    inputs?: Record<string, any>;
  }): Promise<Record<string, any>> => {
    const { data } = await axiosInstance.post<Record<string, any>>("/coordinator/run", payload);
    return data;
  },
};
