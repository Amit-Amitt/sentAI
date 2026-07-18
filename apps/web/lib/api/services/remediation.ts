import { axiosInstance } from "../axios";

export interface RemediationRun {
  id: string;
  incident_id: string;
  status: string;
  fix_strategy?: string[];
  code_patch?: any;
  github_pr_draft?: any;
  rollback_plan?: any;
  risk_analysis?: any;
  runbook?: any;
  created_at?: string;
}

export const remediationService = {
  list: async (workspaceId: string): Promise<RemediationRun[]> => {
    const { data } = await axiosInstance.get<RemediationRun[]>("/remediation", {
      params: { workspace_id: workspaceId },
    });
    return data;
  },

  get: async (workspaceId: string, incidentId: string): Promise<RemediationRun> => {
    const { data } = await axiosInstance.get<RemediationRun>(`/remediation/${incidentId}`, {
      params: { workspace_id: workspaceId },
    });
    return data;
  },

  generate: async (workspaceId: string, incidentId: string): Promise<{ id: string, status: string }> => {
    const { data } = await axiosInstance.post("/remediation/generate", 
      { incident_id: incidentId },
      { params: { workspace_id: workspaceId } }
    );
    return data;
  },
};
