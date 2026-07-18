import structlog

logger = structlog.get_logger("sentinel_api.ai.agents.log_agent.severity")


class SeverityClassifier:
    """Normalizes log finding clusters into standard severity levels."""

    def classify(self, category: str, occurrences: int, max_level: str) -> str:
        """Determines rating (Critical, High, Medium, Low, Informational) based on context."""
        logger.info(
            "Classifying finding severity",
            category=category,
            occurrences=occurrences,
            max_level=max_level,
        )

        # 1. Critical Severity
        if category in ["MEMORY", "DISK"] or max_level in ["CRITICAL", "FATAL"]:
            return "Critical"
        if category == "EXCEPTION" and occurrences >= 5:
            return "Critical"

        # 2. High Severity
        if category in ["CONNECTION", "TIMEOUT", "EXCEPTION"]:
            return "High"
        if category == "HTTP_5XX" and occurrences >= 10:
            return "High"

        # 3. Medium Severity
        if category in ["HTTP_5XX", "AUTHENTICATION"]:
            return "Medium"
        if category == "HTTP_4XX" and occurrences >= 20:
            return "Medium"
        if max_level == "ERROR":
            return "Medium"

        # 4. Low Severity
        if category == "HTTP_4XX" or max_level in ["WARN", "WARNING"]:
            return "Low"

        # 5. Informational Severity
        return "Informational"
