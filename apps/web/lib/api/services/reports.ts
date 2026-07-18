import { axiosInstance } from "../axios";

export const reportsService = {
  getReport: async (incidentId: string): Promise<Record<string, any>> => {
    const { data } = await axiosInstance.get<Record<string, any>>(`/reports/${incidentId}`);
    return data;
  },
};
