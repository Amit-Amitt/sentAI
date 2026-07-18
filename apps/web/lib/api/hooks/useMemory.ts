import { useQuery } from "@tanstack/react-query";
import { memoryService } from "../services/memory";

export function useMemories(workspaceId: string | null | undefined, limit: number = 50, offset: number = 0) {
  return useQuery({
    queryKey: ["memories", workspaceId, limit, offset],
    queryFn: () => {
      if (!workspaceId) throw new Error("Workspace not found");
      return memoryService.listMemories(workspaceId, limit, offset);
    },
    enabled: !!workspaceId,
  });
}

export function useSimilarMemories(workspaceId: string | null | undefined, query: string, limit: number = 5) {
  return useQuery({
    queryKey: ["similarMemories", workspaceId, query, limit],
    queryFn: () => {
      if (!workspaceId) throw new Error("Workspace not found");
      return memoryService.searchSimilar(workspaceId, query, limit);
    },
    enabled: !!workspaceId && !!query && query.length > 2,
  });
}
