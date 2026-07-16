export interface SimulationScenario {
  id: string;
  slug: string;
  name: string;
  description: string;
  difficulty: "easy" | "medium" | "hard";
  estimatedRuntimeSec: number;
  primaryService: string;
}

export interface SimulationRunStatus {
  simulationId: string;
  incidentId?: string;
  status: "queued" | "running" | "completed" | "failed";
  startedAt: string;
  emittedSignalCount: number;
}
