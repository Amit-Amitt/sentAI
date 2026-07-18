import { useQuery } from "@tanstack/react-query";
import { healthService } from "../services/health";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: healthService.getHealth,
    refetchInterval: 30000, // Poll health status every 30 seconds
  });
}
