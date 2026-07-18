import { axiosInstance } from "../axios";
import { HealthResponse } from "../types";

export const healthService = {
  getHealth: async (): Promise<HealthResponse> => {
    const { data } = await axiosInstance.get<HealthResponse>("/health");
    return data;
  },
};
