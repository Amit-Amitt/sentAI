import type { AgentRunSummary } from "./agent";
import type { IncidentSummary } from "./incident";
import type { Severity } from "./common";

export interface SeverityBreakdownItem {
  severity: Severity;
  count: number;
}

export interface ServiceHealthSummary {
  serviceId: string;
  serviceName: string;
  environment: string;
  healthScore: number;
  activeIncidentCount: number;
}

export interface DashboardOverview {
  activeIncidentCount: number;
  severityBreakdown: SeverityBreakdownItem[];
  serviceHealthSummary: ServiceHealthSummary[];
  recentIncidents: IncidentSummary[];
  investigationQueue: AgentRunSummary[];
  latestAgentActivity: AgentRunSummary[];
}
