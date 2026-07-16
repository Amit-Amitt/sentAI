import { z } from "zod";

import {
  confidenceBreakdownSchema,
  hypothesisSchema,
  recommendationSchema,
} from "./agent";
import { incidentStatusSchema, severitySchema } from "./common";

export const serviceRecordSchema = z.object({
  id: z.string(),
  name: z.string(),
  ownerTeam: z.string(),
  tier: z.string(),
  environment: z.string(),
});

export const timelineEntrySchema = z.object({
  id: z.string(),
  incidentId: z.string(),
  eventType: z.string(),
  actorType: z.string(),
  label: z.string(),
  description: z.string(),
  timestamp: z.string(),
  payload: z.record(z.unknown()).optional(),
});

export const incidentSummarySchema = z.object({
  id: z.string(),
  title: z.string(),
  severity: severitySchema,
  status: incidentStatusSchema,
  projectId: z.string(),
  primaryServiceName: z.string().optional(),
  openedAt: z.string(),
  topHypothesisTitle: z.string().optional(),
  topConfidenceScore: z.number().min(0).max(1).optional(),
});

export const incidentDetailSchema = incidentSummarySchema.extend({
  summary: z.string(),
  affectedServices: z.array(serviceRecordSchema),
  rootCauseSummary: z.string().optional(),
  confidenceBreakdown: confidenceBreakdownSchema.optional(),
  topHypothesis: hypothesisSchema.optional(),
  topRecommendations: z.array(recommendationSchema),
  timelinePreview: z.array(timelineEntrySchema),
});
