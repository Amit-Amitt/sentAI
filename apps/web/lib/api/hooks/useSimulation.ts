import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { simulationService, SimulationScenario, SimulationRun, StartSimulationPayload } from "../services/simulation";

const SIMULATION_KEY = "simulation";

export function useScenarios() {
  return useQuery<SimulationScenario[]>({
    queryKey: [SIMULATION_KEY, "scenarios"],
    queryFn: () => simulationService.getScenarios(),
    staleTime: Infinity,
  });
}

export function useSimulationHistory(workspaceId: string | null | undefined) {
  return useQuery<SimulationRun[]>({
    queryKey: [SIMULATION_KEY, "history", workspaceId],
    queryFn: () => simulationService.getHistory(workspaceId!),
    enabled: !!workspaceId,
  });
}

export function useStartSimulation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ workspaceId, payload }: { workspaceId: string; payload: StartSimulationPayload }) =>
      simulationService.startSimulation(workspaceId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [SIMULATION_KEY, "history", variables.workspaceId] });
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
    },
  });
}
