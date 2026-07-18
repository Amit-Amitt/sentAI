from typing import List
import structlog

logger = structlog.get_logger(
    "sentinel_api.ai.agents.review_agent.category_classifier"
)


class CategoryClassifier:
    """Categorizes reports (e.g. Payments, UI, Authentication) using lexicons."""

    def __init__(self) -> None:
        self.rules = {
            "Authentication": [
                "login",
                "logout",
                "signin",
                "signup",
                "password",
                "auth",
                "mfa",
                "token",
                "session",
            ],
            "Checkout": ["checkout", "cart", "basket", "buy", "purchase", "order"],
            "Payments": [
                "payment",
                "pay",
                "billing",
                "invoice",
                "stripe",
                "credit card",
                "charge",
                "refund",
                "card",
            ],
            "Dashboard": [
                "dashboard",
                "chart",
                "metrics",
                "graph",
                "analytics",
                "view",
                "portal",
            ],
            "API": [
                "api",
                "endpoint",
                "graphql",
                "rest",
                "webhook",
                "json",
                "headers",
            ],
            "Database": [
                "database",
                "db",
                "query",
                "postgres",
                "redis",
                "mongodb",
                "sql",
                "migration",
            ],
            "Notifications": [
                "email",
                "sms",
                "alert",
                "notification",
                "slack webhook",
                "webhook alert",
            ],
            "Performance": [
                "slow",
                "speed",
                "timeout",
                "latency",
                "hang",
                "freeze",
                "load time",
                "loading",
            ],
            "Security": [
                "security",
                "vulnerability",
                "leak",
                "permission",
                "unauthorized",
                "hack",
                "secret",
            ],
            "UI": [
                "ui",
                "css",
                "layout",
                "button",
                "align",
                "font",
                "display",
                "page",
                "frontend",
                "color",
            ],
            "Infrastructure": [
                "infra",
                "server",
                "kubernetes",
                "k8s",
                "aws",
                "docker",
                "cluster",
                "cloud",
                "deployment",
            ],
        }

    def classify(self, text: str) -> List[str]:
        """Scans the text against keyword lexicons to return matched categories."""
        logger.debug("Classifying target text category tags")
        text_lower = text.lower()
        matched = []

        for category, keywords in self.rules.items():
            if any(kw in text_lower for kw in keywords):
                matched.append(category)

        if not matched:
            matched.append("Other")

        return matched
