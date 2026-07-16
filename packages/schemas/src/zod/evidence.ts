import { z } from "zod";

import { severitySchema } from "./common";

export const signalEventSchema = z.object({
  id: z.string(),
  incidentId: z.string().optional(),
  serviceId: z.string().optional(),
  signalType: z.enum([
    "alert",
    "log",
    "metric",
    "deployment",
    "customer_feedback",
    "incident_note",
  ]),
  source: z.string(),
  timestamp: z.string(),
  severity: severitySchema,
  payload: z.record(z.unknown()),
  metadata: z.record(z.unknown()).optional(),
});

export const evidenceItemSchema = z.object({
  id: z.string(),
  incidentId: z.string(),
  signalEventId: z.string().optional(),
  evidenceType: z.string(),
  title: z.string(),
  summary: z.string(),
  timestamp: z.string(),
  importanceScore: z.number(),
  serviceName: z.string().optional(),
  attributes: z.record(z.unknown()).optional(),
});

export const deploymentRecordSchema = z.object({
  id: z.string(),
  serviceId: z.string(),
  version: z.string(),
  commitSha: z.string().optional(),
  deployedAt: z.string(),
  changeSummary: z.string(),
  riskLevel: z.enum(["low", "medium", "high"]),
});

export const graphNodeSchema = z.object({
  id: z.string(),
  type: z.string(),
  label: z.string(),
  entityId: z.string(),
  severity: severitySchema.optional(),
  confidenceScore: z.number().min(0).max(1).optional(),
  metadata: z.record(z.unknown()).optional(),
});

export const graphEdgeSchema = z.object({
  id: z.string(),
  source: z.string(),
  target: z.string(),
  relationshipType: z.string(),
  strength: z.number().optional(),
  label: z.string().optional(),
});
