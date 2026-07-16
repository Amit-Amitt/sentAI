import type { ConfidenceBreakdown, Hypothesis, Recommendation } from "./agent";
import type { Severity, IncidentStatus } from "./common";

export interface ServiceRecord {
  id: string;
  name: string;
  ownerTeam: string;
  tier: string;
  environment: string;
}

export interface IncidentSummary {
  id: string;
  title: string;
  severity: Severity;
  status: IncidentStatus;
  projectId: string;
  primaryServiceName?: string;
  openedAt: string;
  topHypothesisTitle?: string;
  topConfidenceScore?: number;
}

export interface TimelineEntry {
  id: string;
  incidentId: string;
  eventType: string;
  actorType: string;
  label: string;
  description: string;
  timestamp: string;
  payload?: Record<string, unknown>;
}

export interface IncidentDetail extends IncidentSummary {
  summary: string;
  affectedServices: ServiceRecord[];
  rootCauseSummary?: string;
  confidenceBreakdown?: ConfidenceBreakdown;
  topHypothesis?: Hypothesis;
  topRecommendations: Recommendation[];
  timelinePreview: TimelineEntry[];
}
