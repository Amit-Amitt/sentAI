import { useQuery } from "@tanstack/react-query";
import { incidentsService } from "../services/incidents";

export function useIncidents(params?: {
  skip?: number;
  limit?: number;
  status?: string;
  sort_by?: string;
  sort_order?: string;
}) {
  return useQuery({
    queryKey: ["incidents", params],
    queryFn: () => incidentsService.listIncidents(params),
    // Poll updates if any incident is in active state
    refetchInterval: (query) => {
      const data = query.state.data;
      const hasActive = data?.results?.some(
        (r) => r.status.toUpperCase() === "ACTIVE" || r.status.toUpperCase() === "PENDING"
      );
      return hasActive ? 5000 : 30000; // poll every 5s if active, otherwise 30s
    },
  });
}
