import { IncidentReport } from "./index";
import { Incident, AgentRunState } from "../../store/use-store";

export function mapReportToIncident(
  report: IncidentReport,
  checkedPlaybookItems: Record<string, boolean> = {}
): Incident {
  // Safe defaults
  const meta = report.metadata || {};
  const exec = report.executive_summary || {};
  const ev = report.evidence || {};
  const rc = report.root_cause || {};
  const recs = report.recommendations || {};
  const plan = report.recovery_plan || {};
  const conf = report.confidence || {};

  // Build mapped recommendations
  const mappedRecommendations: Incident["recommendations"] = [];
  const immediate = recs.immediate_actions || [];
  const shortTerm = recs.short_term_actions || [];
  const longTerm = recs.long_term_improvements || [];

  let recIdx = 1;
  const processActionList = (list: any[], priority: "Critical" | "High" | "Medium" | "Low") => {
    list.forEach((act, i) => {
      mappedRecommendations.push({
        id: act.id || `rec-${priority.toLowerCase()}-${recIdx++}`,
        title: act.title || act.action_name || act.action || `Remediation Step`,
        description: act.description || act.rationale || act.details || "",
        priority,
        execution_order: act.execution_order || recIdx,
      });
    });
  };

  processActionList(immediate, "Critical");
  processActionList(shortTerm, "High");
  processActionList(longTerm, "Medium");

  const incidentId = meta.incident_id || "UNKNOWN";

  // Build mapped recovery checklist
  const mappedChecklist: Incident["recovery_checklist"] = (plan.recovery_checklist || []).map((step, i) => {
    const valStep = (plan.validation_steps || [])[i] || {};
    const key = `${incidentId}-${step}`;
    return {
      title: step,
      command: valStep.command || valStep.action || "",
      success_criteria: valStep.success_criteria || valStep.criteria || "Run completes",
      completed: !!checkedPlaybookItems[key],
    };
  });

  // Reconstruct agent runs
  const agents: Record<string, AgentRunState> = {
    "Coordinator": {
      name: "Coordinator",
      status: "COMPLETED",
      duration_ms: 120,
      confidence: conf.coverage_score || 0.95,
      summary: "Created plan topology.",
      findings: [],
    },
    "Deployment Agent": {
      name: "Deployment Agent",
      status: "COMPLETED",
      duration_ms: 380,
      confidence: conf.agent_confidence_summary?.["Deployment Agent"] || 0.90,
      summary: ev.deployments?.[0] || "Analyzed deployment metadata.",
      findings: (ev.deployments || []).map(d => ({ value: d })),
    },
    "Log Agent": {
      name: "Log Agent",
      status: "COMPLETED",
      duration_ms: 450,
      confidence: conf.agent_confidence_summary?.["Log Agent"] || 0.88,
      summary: ev.logs?.[0] || "Analyzed log archives.",
      findings: (ev.logs || []).map(l => ({ value: l })),
    },
    "Metrics Agent": {
      name: "Metrics Agent",
      status: "COMPLETED",
      duration_ms: 320,
      confidence: conf.agent_confidence_summary?.["Metrics Agent"] || 0.94,
      summary: ev.metrics?.[0] || "Analyzed metrics stream.",
      findings: (ev.metrics || []).map(m => ({ value: m })),
    },
    "Review Agent": {
      name: "Review Agent",
      status: "COMPLETED",
      duration_ms: 610,
      confidence: conf.agent_confidence_summary?.["Review Agent"] || 0.80,
      summary: ev.customer_feedback?.[0] || "Clustered customer feedback tickets.",
      findings: (ev.customer_feedback || []).map(c => ({ value: c })),
    },
    "Root Cause Agent": {
      name: "Root Cause Agent",
      status: "COMPLETED",
      duration_ms: 750,
      confidence: rc.confidence || 0.92,
      summary: rc.primary_root_cause || "Determined root cause driver.",
      findings: [],
    },
    "Recommendation Agent": {
      name: "Recommendation Agent",
      status: "COMPLETED",
      duration_ms: 290,
      confidence: conf.agent_confidence_summary?.["Recommendation Agent"] || 0.90,
      summary: "Generated rollback recommendations.",
      findings: [],
    },
  };

  return {
    id: meta.incident_id || "UNKNOWN",
    severity: (meta.severity || "SEV1") as "SEV1" | "SEV2" | "SEV3",
    status: (meta.status?.toUpperCase() === "RESOLVED" ? "RESOLVED" : "ACTIVE"),
    summary: exec.incident_overview || "No Summary Available",
    description: exec.incident_overview || "No details provided.",
    created_at: meta.created_at || new Date().toISOString(),
    affected_services: meta.affected_services || exec.affected_services || [],
    owner: meta.owner || "on-call-sre",
    confidence: conf.overall_confidence || rc.confidence || 0.0,
    logs: (ev.logs || []).join("\n"),
    metrics: (ev.metrics || []).join("\n"),
    deployment_history: (ev.deployments || []).join("\n"),
    customer_reports: (ev.customer_feedback || []).join("\n"),
    agents,
    root_cause: {
      primary: rc.primary_root_cause || "Pending diagnosis",
      supporting_evidence: rc.supporting_evidence || [],
      alternative_hypotheses: (rc.alternative_hypotheses || []).map((h: any) => ({
        type: h.hypothesis_name || h.type || "Alternative Hypothesis",
        confidence: h.confidence || h.score || 0.5,
        description: h.description || h.rationale || "Possibility under assessment.",
      })),
    },
    recommendations: mappedRecommendations,
    recovery_checklist: mappedChecklist,
  };
}
