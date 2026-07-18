import { useQuery } from "@tanstack/react-query";
import { reportsService } from "../services/reports";

export function useReport(incidentId: string | null | undefined) {
  return useQuery({
    queryKey: ["report", incidentId],
    queryFn: () => {
      if (!incidentId) return null;
      return reportsService.getReport(incidentId);
    },
    enabled: !!incidentId,
  });
}
