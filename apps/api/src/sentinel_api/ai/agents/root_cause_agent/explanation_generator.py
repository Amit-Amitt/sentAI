from typing import List
import structlog

from sentinel_api.ai.agents.root_cause_agent.schemas import (
    RootCauseHypothesis,
    RootCauseSummary,
)

logger = structlog.get_logger(
    "sentinel_api.ai.agents.root_cause_agent.explanation_generator"
)


class ExplanationGenerator:
    """Generates narrative executive summaries, technical descriptions, and reasoning logic."""

    def generate_explanations(
        self,
        ranked_hypotheses: List[RootCauseHypothesis],
        timeline_summary: List[str],
    ) -> RootCauseSummary:
        """Constructs text explanations from ranked hypotheses and event timelines."""
        logger.info("Generating narrative root cause summaries")

        if not ranked_hypotheses:
            return RootCauseSummary(
                executive_explanation="No valid root cause hypotheses identified.",
                technical_explanation=(
                    "Evidence collector was empty or failed to match patterns."
                ),
                evidence_summary="No matching logs, metrics, or deployments.",
                reasoning_summary="No reasoning paths traversed.",
                alternative_explanations=[],
            )

        top_h = ranked_hypotheses[0]

        exec_exp = (
            f"The most likely root cause is determined to be: {top_h.title}"
            f" (Confidence: {top_h.score:.2f}). {top_h.description}"
        )

        tech_exp = (
            f"Technical diagnosis indicates type '{top_h.root_cause_type}'."
            f" Chronological event sequence points to the following supporting"
            f" steps:\n"
            + "\n".join(f"- {ev}" for ev in top_h.supporting_evidence)
        )

        evidence_sum = (
            f"Gathered {len(top_h.supporting_evidence)} supporting indicators."
            f" Event sequence includes:\n"
            + "\n".join(timeline_summary[:5])
        )

        reasoning_sum = (
            f"Evaluated timelines and cross-correlated technical entities."
            f" Matching services/features and temporal sequence supports"
            f" {top_h.title}."
        )

        alternatives = []
        for h in ranked_hypotheses[1:3]:
            alternatives.append(
                f"{h.title} (Score: {h.score:.2f}) - {h.description}"
            )

        return RootCauseSummary(
            executive_explanation=exec_exp,
            technical_explanation=tech_exp,
            evidence_summary=evidence_sum,
            reasoning_summary=reasoning_sum,
            alternative_explanations=alternatives,
        )
