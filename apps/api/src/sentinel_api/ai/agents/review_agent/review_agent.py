import time
from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.review_agent.category_classifier import (
    CategoryClassifier,
)
from sentinel_api.ai.agents.review_agent.entity_extractor import EntityExtractor
from sentinel_api.ai.agents.review_agent.issue_cluster import IssueClusterer
from sentinel_api.ai.agents.review_agent.priority_estimator import PriorityEstimator
from sentinel_api.ai.agents.review_agent.review_parser import ReviewParser
from sentinel_api.ai.agents.review_agent.schemas import (
    ReviewAgentOutput,
    ReviewFinding,
)
from sentinel_api.ai.agents.review_agent.sentiment_analyzer import SentimentAnalyzer
from sentinel_api.ai.agents.review_agent.summarizer import Summarizer
from sentinel_api.ai.agents.review_agent.timeline_builder import TimelineBuilder
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.runtime.agent import BaseAgent
from sentinel_api.ai.schemas.models import AgentRequest

logger = structlog.get_logger("sentinel_api.ai.agents.review_agent.review_agent")


class ReviewAgent(BaseAgent):
    """Processes user reviews, support tickets, and Slack feedback for incident correlations."""

    def __init__(self) -> None:
        super().__init__(name="Review Agent")
        self.parser = ReviewParser()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.category_classifier = CategoryClassifier()
        self.clusterer = IssueClusterer()
        self.entity_extractor = EntityExtractor()
        self.timeline_builder = TimelineBuilder()
        self.priority_estimator = PriorityEstimator()
        self.summarizer = Summarizer()

    def validate(self, request: AgentRequest) -> None:
        """Checks for feedback payloads inside incoming request objects."""
        super().validate(request)

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        reviews = (
            signals.get("customer_feedback")
            or signals.get("tickets")
            or signals.get("reviews")
            or inputs.get("customer_feedback")
            or inputs.get("tickets")
            or inputs.get("reviews")
        )

        if not reviews:
            raise AgentException(
                "Review/feedback data is missing or empty in signals/inputs."
            )

    async def _run(
        self, request: AgentRequest, config: ModelConfig
    ) -> Dict[str, Any]:
        """Runs the complete feedback parsing, categorization, and clustering workflow."""
        start_time = time.perf_counter()

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        raw_reviews = (
            signals.get("customer_feedback")
            or signals.get("tickets")
            or signals.get("reviews")
            or inputs.get("customer_feedback")
            or inputs.get("tickets")
            or inputs.get("reviews")
        )

        # 1. Parse
        items = self.parser.parse(raw_reviews)

        # 2. Sentiment analysis per item
        sentiments = {}
        for item in items:
            sent = self.sentiment_analyzer.analyze_sentiment(item.content)
            sentiments[item.id] = sent

        # 3. Cluster duplicated issue complaints
        clusters = self.clusterer.cluster_issues(items)

        # 4. Form findings from clusters
        findings: List[ReviewFinding] = []
        sentiment_distribution = {
            "Very Positive": 0,
            "Positive": 0,
            "Neutral": 0,
            "Negative": 0,
            "Critical": 0,
        }

        for cluster in clusters:
            cluster_sentiments = [sentiments[item.id] for item in cluster]
            for s in cluster_sentiments:
                sentiment_distribution[s] = (
                    sentiment_distribution.get(s, 0) + 1
                )

            rep_text = cluster[0].content
            categories = self.category_classifier.classify(rep_text)
            category = categories[0]

            features = set()
            for item in cluster:
                ent = self.entity_extractor.extract_entities(item.content)
                features.update(ent["features"])

            priority = self.priority_estimator.estimate_priority(
                cluster, cluster_sentiments
            )

            samples = [item.content[:200] for item in cluster[:3]]
            confidence = min(0.95, 0.70 + 0.05 * len(cluster))

            feat_str = (
                f" Affected features: {', '.join(features)}." if features else ""
            )
            summary_str = f"Found {len(cluster)} reports regarding {category}.{feat_str}"

            findings.append(
                ReviewFinding(
                    category=category,
                    severity=priority["severity"],
                    mentions=len(cluster),
                    affected_features=sorted(list(features)),
                    sample_reports=samples,
                    confidence=confidence,
                    summary=summary_str,
                )
            )

        findings = sorted(findings, key=lambda x: x.mentions, reverse=True)

        # 5. Timeline Stats & Trends
        timeline_stats, detected_trends = self.timeline_builder.analyze_timeline(
            items
        )

        # 6. Synthesize summaries
        summary = self.summarizer.summarize(
            findings, len(items), sentiment_distribution
        )

        confidence_avg = 0.85
        if findings:
            confidence_avg = sum(f.confidence for f in findings) / len(findings)

        duration_ms = (time.perf_counter() - start_time) * 1000

        output = ReviewAgentOutput(
            agent_name=self.name,
            execution_time_ms=duration_ms,
            status="SUCCESS" if items else "PARTIAL_SUCCESS",
            confidence=confidence_avg,
            findings=findings,
            detected_trends=detected_trends,
            issue_categories=[f.category for f in findings],
            summary=summary,
            metadata={
                "reports_parsed": len(items),
                "clusters_identified": len(clusters),
                "sentiment_distribution": sentiment_distribution,
                "timeline_stats": timeline_stats,
            },
        )

        result_dict = output.model_dump()
        result_dict["reasoning_summary"] = summary.executive_summary
        return result_dict
