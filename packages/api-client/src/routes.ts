import { API_PREFIX } from "@sentinel/config";

export const apiRoutes = {
  health: `${API_PREFIX}/health`,
  dashboard: {
    overview: `${API_PREFIX}/dashboard/overview`,
  },
  incidents: {
    list: `${API_PREFIX}/incidents`,
    detail: (incidentId: string) => `${API_PREFIX}/incidents/${incidentId}`,
    acknowledge: (incidentId: string) => `${API_PREFIX}/incidents/${incidentId}/acknowledge`,
    investigate: (incidentId: string) => `${API_PREFIX}/incidents/${incidentId}/investigate`,
    resolve: (incidentId: string) => `${API_PREFIX}/incidents/${incidentId}/resolve`,
  },
  simulations: {
    list: `${API_PREFIX}/simulations`,
    run: `${API_PREFIX}/simulations/run`,
    detail: (simulationId: string) => `${API_PREFIX}/simulations/${simulationId}`,
  },
  agentRuns: {
    detail: (runId: string) => `${API_PREFIX}/agent-runs/${runId}`,
    stream: (runId: string) => `${API_PREFIX}/agent-runs/${runId}/stream`,
  },
} as const;
