import { axiosInstance } from "../axios";

export interface SimulationScenario {
  id: string;
  title: string;
  description: string;
  affected_services: string[];
  expected_root_cause: string;
}

export interface SimulationRun {
  id: string;
  incident_id: string;
  scenario_id: string;
  severity: string;
  status: string;
  created_at: string;
}

export interface StartSimulationPayload {
  scenario_id: string;
  severity: string;
}

export const simulationService = {
  getScenarios: async (): Promise<SimulationScenario[]> => {
    const { data } = await axiosInstance.get<SimulationScenario[]>("/simulation/scenarios");
    return data;
  },

  getHistory: async (workspaceId: string): Promise<SimulationRun[]> => {
    const { data } = await axiosInstance.get<SimulationRun[]>("/simulation/history", {
      params: { workspace_id: workspaceId },
    });
    return data;
  },

  startSimulation: async (workspaceId: string, payload: StartSimulationPayload): Promise<SimulationRun> => {
    const { data } = await axiosInstance.post<SimulationRun>("/simulation/start", payload, {
      params: { workspace_id: workspaceId },
    });
    return data;
  },
};
