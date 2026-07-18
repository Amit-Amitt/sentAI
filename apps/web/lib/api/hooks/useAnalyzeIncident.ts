import { useMutation, useQueryClient } from "@tanstack/react-query";
import { incidentsService } from "../services/incidents";
import { IncidentAnalyzeRequest } from "../types";

export function useAnalyzeIncident() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: IncidentAnalyzeRequest) =>
      incidentsService.analyzeIncident(payload),
    onSuccess: (data) => {
      // Invalidate both the master list and detailed keys
      queryClient.invalidateQueries({ queryKey: ["incidents"] });
      queryClient.invalidateQueries({ queryKey: ["incident", data.incident_id] });
      queryClient.invalidateQueries({ queryKey: ["incident", data.investigation_id] });
    },
  });
}
