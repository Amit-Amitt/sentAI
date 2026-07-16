export const PROMPT_IDS = {
  coordinator: "coordinator",
  deployment: "deployment",
  log: "log",
  metrics: "metrics",
  recommendation: "recommendation",
  review: "review",
  rootCause: "root-cause",
} as const;

export const PROMPT_TEMPLATES = {
  coordinator: "src/templates/coordinator.md",
  deployment: "src/templates/deployment.md",
  log: "src/templates/log.md",
  metrics: "src/templates/metrics.md",
  recommendation: "src/templates/recommendation.md",
  review: "src/templates/review.md",
  rootCause: "src/templates/root-cause.md",
} as const;
