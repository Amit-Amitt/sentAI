export const SEVERITIES = ["P1", "P2", "P3", "P4"] as const;
export type Severity = (typeof SEVERITIES)[number];

export const INCIDENT_STATUSES = [
  "open",
  "investigating",
  "mitigating",
  "monitoring",
  "resolved",
  "needs-human-review",
] as const;
export type IncidentStatus = (typeof INCIDENT_STATUSES)[number];

export const SIGNAL_TYPES = [
  "alert",
  "log",
  "metric",
  "deployment",
  "customer_feedback",
  "incident_note",
] as const;
export type SignalType = (typeof SIGNAL_TYPES)[number];

export const AGENT_NAMES = [
  "coordinator",
  "log",
  "metrics",
  "deployment",
  "review",
  "root_cause",
  "recommendation",
] as const;
export type AgentName = (typeof AGENT_NAMES)[number];

export const RECOMMENDATION_CATEGORIES = [
  "immediate",
  "short_term",
  "long_term",
] as const;
export type RecommendationCategory = (typeof RECOMMENDATION_CATEGORIES)[number];

export const RUN_STATUSES = [
  "queued",
  "planning",
  "running",
  "completed",
  "degraded",
  "failed",
  "needs-human-review",
] as const;
export type RunStatus = (typeof RUN_STATUSES)[number];

export const RISK_LEVELS = ["low", "medium", "high"] as const;
export type RiskLevel = (typeof RISK_LEVELS)[number];
