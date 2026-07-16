import { z } from "zod";

import { agentNameSchema, recommendationCategorySchema, runStatusSchema } from "./common";

export const confidenceBreakdownSchema = z.object({
  overall: z.number().min(0).max(1),
  evidenceQuality: z.number().min(0).max(1),
  crossAgentAgreement: z.number().min(0).max(1),
  temporalAlignment: z.number().min(0).max(1),
  modelCertainty: z.number().min(0).max(1),
  contradictionPenalty: z.number().min(0).max(1),
  notes: z.array(z.string()),
});

export const agentRunSummarySchema = z.object({
  id: z.string(),
  incidentId: z.string(),
  agentName: agentNameSchema,
  status: runStatusSchema,
  startedAt: z.string().optional(),
  completedAt: z.string().optional(),
  attempt: z.number().int().nonnegative(),
  confidenceScore: z.number().min(0).max(1).optional(),
});

export const agentFindingSchema = z.object({
  id: z.string(),
  agentRunId: z.string(),
  title: z.string(),
  summary: z.string(),
  findingType: z.string(),
  supportingEvidenceIds: z.array(z.string()),
  contradictingEvidenceIds: z.array(z.string()),
  confidenceScore: z.number().min(0).max(1),
  openQuestions: z.array(z.string()),
});

export const hypothesisSchema = z.object({
  id: z.string(),
  incidentId: z.string(),
  rank: z.number().int().positive(),
  title: z.string(),
  summary: z.string(),
  confidenceScore: z.number().min(0).max(1),
  supportingEvidenceIds: z.array(z.string()),
  contradictingEvidenceIds: z.array(z.string()),
  status: z.enum(["candidate", "selected", "rejected"]),
});

export const recommendationSchema = z.object({
  id: z.string(),
  incidentId: z.string(),
  hypothesisId: z.string().optional(),
  category: recommendationCategorySchema,
  priority: z.number().int().nonnegative(),
  title: z.string(),
  description: z.string(),
  riskLevel: z.enum(["low", "medium", "high"]),
  reversibility: z.enum(["reversible", "partially_reversible", "hard_to_reverse"]),
  confidenceScore: z.number().min(0).max(1),
});
