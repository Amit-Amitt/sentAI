import { z } from "zod";

import { agentRunSummarySchema } from "./agent";
import { severitySchema } from "./common";
import { incidentSummarySchema } from "./incident";

export const severityBreakdownItemSchema = z.object({
  severity: severitySchema,
  count: z.number().int().nonnegative(),
});

export const serviceHealthSummarySchema = z.object({
  serviceId: z.string(),
  serviceName: z.string(),
  environment: z.string(),
  healthScore: z.number().min(0).max(100),
  activeIncidentCount: z.number().int().nonnegative(),
});

export const dashboardOverviewSchema = z.object({
  activeIncidentCount: z.number().int().nonnegative(),
  severityBreakdown: z.array(severityBreakdownItemSchema),
  serviceHealthSummary: z.array(serviceHealthSummarySchema),
  recentIncidents: z.array(incidentSummarySchema),
  investigationQueue: z.array(agentRunSummarySchema),
  latestAgentActivity: z.array(agentRunSummarySchema),
});
