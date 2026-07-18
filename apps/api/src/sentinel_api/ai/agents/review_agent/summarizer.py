from typing import Dict, List
import structlog

from sentinel_api.ai.agents.review_agent.schemas import ReviewFinding, ReviewSummary

logger = structlog.get_logger("sentinel_api.ai.agents.review_agent.summarizer")


class Summarizer:
    """Narrates ticket reviews, describing user/business impact details."""

    def summarize(
        self,
        findings: List[ReviewFinding],
        total_reports: int,
        sentiment_distribution: Dict[str, int],
    ) -> ReviewSummary:
        """Constructs text summary blocks from cluster statistics."""
        logger.info("Summarizing processed reviews findings")

        negatives = sentiment_distribution.get(
            "Negative", 0
        ) + sentiment_distribution.get("Critical", 0)
        neg_pct = int(negatives / total_reports * 100) if total_reports > 0 else 0

        exec_sum = (
            f"Analyzed {total_reports} customer reports."
            f" Identified {len(findings)} distinct issue categories."
            f" Sentiment skew: {neg_pct}% of the reports contain"
            " negative/critical sentiment."
        )

        categories_str = ", ".join(f.category for f in findings)
        detailed_findings = f"Issues classified across categories: {categories_str}."
        for f in findings:
            detailed_findings += (
                f"\n- {f.category} (Mentions: {f.mentions}, Severity:"
                f" {f.severity}): {f.summary}"
            )

        user_impact = "Users are encountering errors that degrade system usability."
        if any(f.severity == "Critical" for f in findings):
            user_impact = (
                "Critical blocking issues prevent users from finishing key"
                " application actions."
            )

        business_impact = "Low business risk."
        core_findings = [
            f
            for f in findings
            if f.category in ["Payments", "Checkout", "Authentication"]
        ]
        if core_findings:
            severity_list = [f.severity for f in core_findings]
            if "Critical" in severity_list or "High" in severity_list:
                business_impact = (
                    "High business operational risk: key customer conversion"
                    " pathways are broken."
                )
            else:
                business_impact = (
                    "Medium business risk: minor issues in checkout/auth flows."
                )

        potential_contributors = []
        for f in findings:
            if f.severity in ["High", "Critical"]:
                potential_contributors.append(
                    f"Possible outage or bug in service/feature relating to"
                    f" {f.category} ({', '.join(f.affected_features)})."
                )
        if not potential_contributors:
            potential_contributors.append(
                "No high-severity user-facing issues identified."
            )

        return ReviewSummary(
            executive_summary=exec_sum,
            detailed_findings=detailed_findings,
            user_impact_summary=user_impact,
            business_impact_summary=business_impact,
            potential_contributors=potential_contributors,
        )
