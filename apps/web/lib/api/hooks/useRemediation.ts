import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { remediationService } from "../services/remediation";

export function useRemediations(workspaceId?: string) {
  return useQuery({
    queryKey: ["remediations", workspaceId],
    queryFn: () => remediationService.list(workspaceId!),
    enabled: !!workspaceId,
  });
}

export function useRemediation(workspaceId?: string, incidentId?: string) {
  return useQuery({
    queryKey: ["remediation", workspaceId, incidentId],
    queryFn: () => remediationService.get(workspaceId!, incidentId!),
    enabled: !!workspaceId && !!incidentId,
    retry: false, // Don't retry if 404
  });
}

export function useGenerateRemediation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ workspaceId, incidentId }: { workspaceId: string; incidentId: string }) =>
      remediationService.generate(workspaceId, incidentId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["remediation", variables.workspaceId, variables.incidentId] });
      queryClient.invalidateQueries({ queryKey: ["remediations", variables.workspaceId] });
    },
  });
}
