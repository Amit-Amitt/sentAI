from typing import Dict
import structlog

logger = structlog.get_logger(
    "sentinel_api.ai.agents.review_agent.sentiment_analyzer"
)


class SentimentAnalyzer:
    """Classifies user feedback text into positive/negative/critical sentiment groups."""

    def analyze_sentiment(self, text: str) -> str:
        """Determines sentiment using a rule-based lexicon match."""
        logger.debug("Evaluating textual sentiment profile")
        text_lower = text.lower()

        critical_words = [
            "critical",
            "crash",
            "broken",
            "severe",
            "down",
            "emergency",
            "fatal",
            "outage",
            "blocker",
        ]
        negative_words = [
            "error",
            "bug",
            "fail",
            "slow",
            "wrong",
            "cannot",
            "cant",
            "issue",
            "problem",
            "bad",
            "terrible",
            "hate",
            "worst",
            "timeout",
            "latency",
        ]
        very_positive_words = [
            "fantastic",
            "amazing",
            "extraordinary",
            "perfectly",
            "love it",
            "excellent",
            "best",
        ]
        positive_words = [
            "great",
            "good",
            "happy",
            "love",
            "awesome",
            "perfect",
            "thanks",
            "fine",
        ]

        if any(w in text_lower for w in critical_words):
            return "Critical"
        if any(w in text_lower for w in negative_words):
            return "Negative"
        if any(w in text_lower for w in very_positive_words):
            return "Very Positive"
        if any(w in text_lower for w in positive_words):
            return "Positive"

        return "Neutral"
