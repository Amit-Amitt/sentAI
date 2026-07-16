import { z } from "zod";

export const severitySchema = z.enum(["P1", "P2", "P3", "P4"]);

export const incidentStatusSchema = z.enum([
  "open",
  "investigating",
  "mitigating",
  "monitoring",
  "resolved",
  "needs-human-review",
]);

export const agentNameSchema = z.enum([
  "coordinator",
  "log",
  "metrics",
  "deployment",
  "review",
  "root_cause",
  "recommendation",
]);

export const recommendationCategorySchema = z.enum([
  "immediate",
  "short_term",
  "long_term",
]);

export const runStatusSchema = z.enum([
  "queued",
  "planning",
  "running",
  "completed",
  "degraded",
  "failed",
  "needs-human-review",
]);
