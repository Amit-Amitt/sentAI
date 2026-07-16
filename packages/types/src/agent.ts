import type { AgentName, RecommendationCategory, RiskLevel, RunStatus } from "./common";

export interface AgentRunSummary {
  id: string;
  incidentId: string;
  agentName: AgentName;
  status: RunStatus;
  startedAt?: string;
  completedAt?: string;
  attempt: number;
  confidenceScore?: number;
}

export interface AgentFinding {
  id: string;
  agentRunId: string;
  title: string;
  summary: string;
  findingType: string;
  supportingEvidenceIds: string[];
  contradictingEvidenceIds: string[];
  confidenceScore: number;
  openQuestions: string[];
}

export interface ConfidenceBreakdown {
  overall: number;
  evidenceQuality: number;
  crossAgentAgreement: number;
  temporalAlignment: number;
  modelCertainty: number;
  contradictionPenalty: number;
  notes: string[];
}

export interface Hypothesis {
  id: string;
  incidentId: string;
  rank: number;
  title: string;
  summary: string;
  confidenceScore: number;
  supportingEvidenceIds: string[];
  contradictingEvidenceIds: string[];
  status: "candidate" | "selected" | "rejected";
}

export interface Recommendation {
  id: string;
  incidentId: string;
  hypothesisId?: string;
  category: RecommendationCategory;
  priority: number;
  title: string;
  description: string;
  riskLevel: RiskLevel;
  reversibility: "reversible" | "partially_reversible" | "hard_to_reverse";
  confidenceScore: number;
}
