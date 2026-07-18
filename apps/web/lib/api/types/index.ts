export * from "./organization";

export interface HealthResponse {
  status: string;
  version: string;
}

export interface IncidentAnalyzeRequest {
  incident_id: string;
  severity: string;
  status: string;
  summary: string;
  logs?: any;
  metrics?: any;
  deployment_history?: any;
  customer_reports?: any;
}

export interface AnalysisSubmitResponse {
  investigation_id: string;
  status: string;
  incident_id: string;
}

export interface InvestigationRecord {
  id: string;
  incident_id: string;
  severity: string;
  status: string;
  summary: string;
  created_at?: string;
  updated_at?: string;
  confidence?: number;
}

export interface InvestigationListResponse {
  results: InvestigationRecord[];
  total: number;
  skip: number;
  limit: number;
}

export interface ReportMetadata {
  incident_id: string;
  severity: string;
  status: string;
  created_at: string;
  owner: string;
  affected_services: string[];
}

export interface ReportExecutiveSummary {
  incident_overview: string;
  affected_services: string[];
  severity: string;
  business_impact: string;
  investigation_status: string;
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  description: string;
  details: Record<string, any>;
}

export interface EvidenceSummary {
  logs: string[];
  metrics: string[];
  deployments: string[];
  customer_feedback: string[];
}

export interface RootCauseSection {
  primary_root_cause: string;
  supporting_evidence: string[];
  alternative_hypotheses: Array<Record<string, any>>;
  confidence: number;
}

export interface RecommendationSection {
  immediate_actions: Array<Record<string, any>>;
  short_term_actions: Array<Record<string, any>>;
  long_term_improvements: Array<Record<string, any>>;
  priority: string;
  risk: string;
}

export interface RecoveryPlanSection {
  recovery_checklist: string[];
  validation_steps: Array<Record<string, any>>;
  monitoring_plan: Record<string, any>;
}

export interface ConfidenceSummarySection {
  overall_confidence: number;
  evidence_quality: number;
  coverage_score: number;
  agent_confidence_summary: Record<string, number>;
}

export interface IncidentReport {
  metadata: ReportMetadata;
  executive_summary: ReportExecutiveSummary;
  timeline: TimelineEvent[];
  evidence: EvidenceSummary;
  root_cause: RootCauseSection;
  recommendations: RecommendationSection;
  recovery_plan: RecoveryPlanSection;
  confidence: ConfidenceSummarySection;
  raw_metadata: Record<string, any>;
}
