import { useQuery } from "@tanstack/react-query";
import { incidentsService } from "../services/incidents";
import { mapReportToIncident } from "../types/mapper";
import { useStore } from "../../store/use-store";

export function useIncident(incidentId: string | null | undefined) {
  return useQuery({
    queryKey: ["incident", incidentId],
    queryFn: async () => {
      if (!incidentId) return null;
      const report = await incidentsService.getIncident(incidentId);
      const checkedPlaybookItems = useStore.getState().checkedPlaybookItems;
      return mapReportToIncident(report, checkedPlaybookItems);
    },
    enabled: !!incidentId,
    refetchInterval: (query) => {
      const data = query.state.data;
      // Fast polling if the incident diagnosis is currently active
      if (data && data.status === "ACTIVE") {
        return 3000;
      }
      return false;
    },
  });
}
