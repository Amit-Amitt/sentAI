import type { RiskLevel, Severity, SignalType } from "./common";

export interface SignalEvent {
  id: string;
  incidentId?: string;
  serviceId?: string;
  signalType: SignalType;
  source: string;
  timestamp: string;
  severity: Severity;
  payload: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface EvidenceItem {
  id: string;
  incidentId: string;
  signalEventId?: string;
  evidenceType: string;
  title: string;
  summary: string;
  timestamp: string;
  importanceScore: number;
  serviceName?: string;
  attributes?: Record<string, unknown>;
}

export interface DeploymentRecord {
  id: string;
  serviceId: string;
  version: string;
  commitSha?: string;
  deployedAt: string;
  changeSummary: string;
  riskLevel: RiskLevel;
}

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  entityId: string;
  severity?: Severity;
  confidenceScore?: number;
  metadata?: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationshipType: string;
  strength?: number;
  label?: string;
}
