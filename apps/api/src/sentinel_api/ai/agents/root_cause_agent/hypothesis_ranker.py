from typing import List
import structlog

from sentinel_api.ai.agents.root_cause_agent.schemas import RootCauseHypothesis

logger = structlog.get_logger(
    "sentinel_api.ai.agents.root_cause_agent.hypothesis_ranker"
)


class HypothesisRanker:
    """Ranks hypotheses using evidence volume, confidence, and chronological logic."""

    def rank_hypotheses(
        self, hypotheses: List[RootCauseHypothesis]
    ) -> List[RootCauseHypothesis]:
        """Updates and sorts hypotheses by a calculated scoring formula."""
        logger.info("Ranking candidate hypotheses")

        for h in hypotheses:
            evidence_count = len(h.supporting_evidence)
            score = (
                h.confidence + (0.05 * evidence_count)
            ) * h.timeline_consistency
            h.score = min(1.0, max(0.0, score))

        ranked = sorted(hypotheses, key=lambda x: x.score, reverse=True)
        return ranked
