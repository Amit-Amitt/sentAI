import structlog

from sentinel_api.ai.agents.review_agent.utils import tokenize

logger = structlog.get_logger(
    "sentinel_api.ai.agents.review_agent.duplicate_detector"
)


class DuplicateDetector:
    """Calculates text overlap ratios to flag duplicate customer reports."""

    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold

    def is_duplicate(self, text_a: str, text_b: str) -> bool:
        """Determines if text_b is a duplicate of text_a based on token Jaccard Index."""
        logger.debug("Checking for duplicate content")
        if text_a.strip().lower() == text_b.strip().lower():
            return True

        tokens_a = tokenize(text_a)
        tokens_b = tokenize(text_b)

        if not tokens_a or not tokens_b:
            return False

        union = tokens_a | tokens_b
        intersection = tokens_a & tokens_b

        score = len(intersection) / len(union)
        return score >= self.threshold
