from sentinel_api.app.reporting.schemas import IncidentReport
from sentinel_api.app.reporting.utils import format_timestamp_friendly


class MarkdownExporter:
    """Exports the unified Incident Report to GitHub Flavored Markdown."""

    def export(self, report: IncidentReport) -> str:
        """Translates the IncidentReport model properties to rich markdown layout."""
        md = []

        md.append(f"# Sentinel AI Incident Report: {report.metadata.incident_id}")
        md.append("")
        md.append(
            f"**Severity**: `{report.metadata.severity}` | **Status**:"
            f" `{report.metadata.status}` | **Owner**:"
            f" `{report.metadata.owner}`"
        )
        md.append(
            f"**Created At**: {format_timestamp_friendly(report.metadata.created_at)}"
        )
        md.append("")

        md.append("## 1. Executive Summary")
        md.append(f"> {report.executive_summary.incident_overview}")
        md.append("")
        services = (
            ", ".join(report.executive_summary.affected_services)
            if report.executive_summary.affected_services
            else "None"
        )
        md.append(f"- **Affected Services**: {services}")
        md.append(f"- **Business Impact**: {report.executive_summary.business_impact}")
        md.append(
            f"- **Status Summary**: {report.executive_summary.investigation_status}"
        )
        md.append("")

        md.append("## 2. Chronological Timeline")
        md.append("| Timestamp | Source | Event Description |")
        md.append("| :--- | :--- | :--- |")
        for event in report.timeline:
            friendly_ts = format_timestamp_friendly(event.timestamp)
            md.append(
                f"| {friendly_ts} | `{event.event_type}` | {event.description} |"
            )
        md.append("")

        md.append("## 3. Telemetry Evidence Summary")

        md.append("### Log Events")
        if report.evidence.logs:
            for log in report.evidence.logs:
                md.append(f"- {log}")
        else:
            md.append("*No critical log events reported.*")
        md.append("")

        md.append("### Metric Anomalies")
        if report.evidence.metrics:
            for met in report.evidence.metrics:
                md.append(f"- {met}")
        else:
            md.append("*No metric anomalies detected.*")
        md.append("")

        md.append("### Deployment History")
        if report.evidence.deployments:
            for dep in report.evidence.deployments:
                md.append(f"- {dep}")
        else:
            md.append("*No recent deployment history correlated.*")
        md.append("")

        md.append("### Customer Support & Feedback")
        if report.evidence.customer_feedback:
            for feed in report.evidence.customer_feedback:
                md.append(f"- {feed}")
        else:
            md.append("*No customer tickets reported during timeline window.*")
        md.append("")

        md.append("## 4. Root Cause Deduction")
        md.append(
            f"**Primary Diagnosis**: **{report.root_cause.primary_root_cause}**"
        )
        md.append(
            f"**Diagnosis Confidence**: `{report.root_cause.confidence * 100:.1f}%`"
        )
        md.append("")
        md.append("### Supporting Heuristics")
        for heur in report.root_cause.supporting_evidence:
            md.append(f"- {heur}")
        md.append("")
        md.append("### Alternative Hypotheses")
        if report.root_cause.alternative_hypotheses:
            for hyp in report.root_cause.alternative_hypotheses:
                md.append(
                    f"- **{hyp.get('root_cause_type')}** (Confidence:"
                    f" `{hyp.get('confidence', 0.0) * 100:.1f}%`):"
                    f" {hyp.get('description')}"
                )
        else:
            md.append("*No alternative hypotheses generated.*")
        md.append("")

        md.append("## 5. Prioritized Recommendations")
        md.append(
            f"**Incident Priority**: `{report.recommendations.priority}` |"
            f" **Execution Risk**: `{report.recommendations.risk}`"
        )
        md.append("")

        md.append("### Immediate Actions")
        if report.recommendations.immediate_actions:
            for act in report.recommendations.immediate_actions:
                md.append(
                    f"1. **{act.get('title')}** (Order:"
                    f" {act.get('execution_order')})"
                )
                md.append(f"   - *Description*: {act.get('description')}")
                md.append(f"   - *Impact*: {act.get('estimated_impact')}")
        else:
            md.append("*No immediate actions required.*")
        md.append("")

        md.append("### Short-Term Actions")
        if report.recommendations.short_term_actions:
            for act in report.recommendations.short_term_actions:
                md.append(
                    f"- **{act.get('title')}**: {act.get('description')}"
                )
        else:
            md.append("*No short-term actions required.*")
        md.append("")

        md.append("### Long-Term Improvements")
        if report.recommendations.long_term_improvements:
            for act in report.recommendations.long_term_improvements:
                md.append(
                    f"- **{act.get('title')}**: {act.get('description')}"
                )
        else:
            md.append("*No long-term actions required.*")
        md.append("")

        md.append("## 6. Recovery & Verification Plan")

        md.append("### Pre-Execution Validation Checks")
        if report.recovery_plan.validation_steps:
            for val in report.recovery_plan.validation_steps:
                md.append(f"- **{val.get('title')}**")
                md.append(f"  - Command: `{val.get('command_suggestion')}`")
                md.append(
                    f"  - Success Criteria: *{val.get('success_criteria')}*"
                )
        else:
            md.append("*No validation steps recommended.*")
        md.append("")

        md.append("### Recovery Checklist")
        for item in report.recovery_plan.recovery_checklist:
            md.append(f"- [ ] {item}")
        md.append("")

        md.append("### Post-Recovery Monitoring")
        watch = ", ".join(
            report.recovery_plan.monitoring_plan.get("metrics_to_watch", [])
        )
        md.append(f"- **Metrics to Watch**: {watch}")
        duration = report.recovery_plan.monitoring_plan.get(
            "duration_minutes", 0
        )
        md.append(f"- **Observation Duration**: `{duration} minutes`")
        md.append(
            f"- **Success Criteria**:"
            f" *{report.recovery_plan.monitoring_plan.get('success_criteria')}*"
        )
        md.append("")

        md.append("## 7. Pipeline Confidence Analytics")
        md.append(
            f"- **Overall Pipeline Confidence**:"
            f" `{report.confidence.overall_confidence * 100:.1f}%`"
        )
        md.append(
            f"- **Evidence Source Quality**:"
            f" `{report.confidence.evidence_quality * 100:.1f}%`"
        )
        md.append(
            f"- **Agent Run Coverage Score**:"
            f" `{report.confidence.coverage_score * 100:.1f}%`"
        )
        md.append("")
        md.append("### Agent Execution Log")
        for ag, conf in report.confidence.agent_confidence_summary.items():
            md.append(f"- `{ag}`: `{conf * 100:.1f}%` confidence status.")

        return "\n".join(md)
