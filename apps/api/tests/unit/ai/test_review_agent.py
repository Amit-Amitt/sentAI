import pytest
from datetime import datetime, UTC, timedelta
from sentinel_api.ai.agents.review_agent import ReviewAgent
from sentinel_api.ai.agents.review_agent.schemas import ReviewItem
from sentinel_api.ai.agents.review_agent.review_parser import ReviewParser
from sentinel_api.ai.agents.review_agent.sentiment_analyzer import SentimentAnalyzer
from sentinel_api.ai.agents.review_agent.category_classifier import CategoryClassifier
from sentinel_api.ai.agents.review_agent.duplicate_detector import DuplicateDetector
from sentinel_api.ai.agents.review_agent.issue_cluster import IssueClusterer
from sentinel_api.ai.agents.review_agent.entity_extractor import EntityExtractor
from sentinel_api.ai.agents.review_agent.timeline_builder import TimelineBuilder
from sentinel_api.ai.agents.review_agent.priority_estimator import PriorityEstimator
from sentinel_api.ai.agents.review_agent.summarizer import Summarizer
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.schemas.models import (
    AgentRequest,
    ExecutionContext,
    IncidentContext,
)


@pytest.fixture
def sample_reviews():
    now = datetime.now(UTC)
    return [
        {
            "id": "t-1",
            "source": "Support Ticket",
            "text": "Cannot login to dashboard, password reset screen is broken",
            "timestamp": (now - timedelta(minutes=15)).isoformat(),
        },
        {
            "id": "t-2",
            "source": "Support Ticket",
            "text": "Login page resets when I submit my mfa credentials",
            "timestamp": (now - timedelta(minutes=14)).isoformat(),
        },
        {
            "id": "t-3",
            "source": "Support Ticket",
            "text": "Checkout payment is slow, /pay/charge took 10s and then failed with 500 error",
            "timestamp": (now - timedelta(minutes=12)).isoformat(),
        },
        {
            "id": "t-4",
            "source": "Slack Message",
            "text": "Checkout page is slow, loading circles spinning forever",
            "timestamp": (now - timedelta(minutes=10)).isoformat(),
        },
        {
            "id": "t-5",
            "source": "GitHub Issue",
            "text": "MFA login is broken for chrome users",
            "timestamp": (now - timedelta(minutes=8)).isoformat(),
        },
    ]


def test_review_parser(sample_reviews):
    parser = ReviewParser()
    items = parser.parse(sample_reviews)

    assert len(items) == 5
    assert items[0].id == "t-1"
    assert items[0].source == "Support Ticket"
    assert "login" in items[0].content


def test_sentiment_analyzer():
    analyzer = SentimentAnalyzer()

    assert analyzer.analyze_sentiment("Everything is amazing, thank you!") == "Very Positive"
    assert analyzer.analyze_sentiment("It is fine, standard behavior.") == "Positive"
    assert analyzer.analyze_sentiment("This checkout page is slow and keeps failing.") == "Negative"
    assert analyzer.analyze_sentiment("System outage! Critical error in database connection.") == "Critical"
    assert analyzer.analyze_sentiment("Normal report.") == "Neutral"


def test_category_classifier():
    classifier = CategoryClassifier()

    assert "Authentication" in classifier.classify("I cannot login to my account.")
    assert "Payments" in classifier.classify("Stripe charged my card twice.")
    assert "Performance" in classifier.classify("Dashboard graphs are loading slowly.")


def test_duplicate_detector():
    detector = DuplicateDetector(threshold=0.4)

    text_a = "Checkout payment is failing with a 500 internal server error"
    text_b = "Checkout page is slow and failing with a 500 internal server error"
    text_c = "MFA login is broken for chrome users"

    # text_a and text_b share tokens: checkout, failing, 500, internal, server, error
    assert detector.is_duplicate(text_a, text_b) is True
    assert detector.is_duplicate(text_a, text_c) is False


def test_issue_clusterer(sample_reviews):
    parser = ReviewParser()
    clusterer = IssueClusterer(threshold=0.4)

    items = parser.parse(sample_reviews)
    clusters = clusterer.cluster_issues(items)

    # login/MFA tickets should cluster together, checkout slow tickets together
    assert len(clusters) >= 2


def test_entity_extractor():
    extractor = EntityExtractor()

    text = "Checkout page is slow, /pay/charge took 10s and then failed with 500 Internal Server error on iOS Chrome"
    entities = extractor.extract_entities(text)

    assert "checkout page" in entities["features"]
    assert "/pay/charge" in entities["endpoints"]
    assert "iOS" in entities["platforms"]
    assert "Chrome" in entities["browsers"]
    assert any("500" in err for err in entities["errors"])


def test_priority_estimator(sample_reviews):
    parser = ReviewParser()
    estimator = PriorityEstimator()

    items = parser.parse(sample_reviews)
    # Cluster relating to payments/checkout
    priority = estimator.estimate_priority(items[2:4], ["Negative", "Critical"])

    # Checkout & payments should upgrade severity to Critical
    assert priority["severity"] == "Critical"
    assert priority["business_impact"] == "High"


def test_timeline_builder(sample_reviews):
    parser = ReviewParser()
    builder = TimelineBuilder()

    items = parser.parse(sample_reviews)
    stats, trends = builder.analyze_timeline(items)

    assert stats["first_report"] is not None
    assert len(trends) >= 1
    assert any(t.trend_type in ["RECURRING", "VOL_GROWTH", "SPIKE"] for t in trends)


@pytest.mark.asyncio
async def test_review_agent_end_to_end(sample_reviews):
    agent = ReviewAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-rev-1",
        correlation_id="corr-rev-2",
        agent_id="test-rev-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-rev-3",
        severity="SEV1",
        status="active",
        summary="User support spike",
        signals={"customer_feedback": sample_reviews}
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)

    assert result.success is True
    assert result.output["agent_name"] == "Review Agent"
    assert len(result.output["findings"]) >= 2
    assert "Authentication" in result.output["issue_categories"]
    assert result.output["summary"]["executive_summary"].startswith("Analyzed 5 customer reports")


@pytest.mark.asyncio
async def test_review_agent_validation_failures():
    agent = ReviewAgent()
    config = ModelConfig(provider="openai", model_name="gpt-4")

    execution_context = ExecutionContext(
        request_id="req-rev-1",
        correlation_id="corr-rev-2",
        agent_id="test-rev-agent",
    )
    incident_context = IncidentContext(
        incident_id="inc-rev-3",
        severity="SEV1",
        status="active",
        summary="No feedback signals"
    )
    request = AgentRequest(
        execution_context=execution_context,
        incident_context=incident_context,
        inputs={}
    )

    result = await agent.execute(request, config)
    assert result.success is False
    assert "Review/feedback data is missing" in result.reasoning_summary
