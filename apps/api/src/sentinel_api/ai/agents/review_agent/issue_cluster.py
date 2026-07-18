from typing import List
import structlog

from sentinel_api.ai.agents.review_agent.duplicate_detector import DuplicateDetector
from sentinel_api.ai.agents.review_agent.schemas import ReviewItem

logger = structlog.get_logger("sentinel_api.ai.agents.review_agent.issue_cluster")


class IssueClusterer:
    """Clusters feedback reports into groups based on near-duplicate Jaccard similarity."""

    def __init__(self, threshold: float = 0.5) -> None:
        self.detector = DuplicateDetector(threshold)

    def cluster_issues(self, items: List[ReviewItem]) -> List[List[ReviewItem]]:
        """Groups ReviewItems, matching each against cluster representatives."""
        logger.info("Clustering feedback items")
        clusters: List[List[ReviewItem]] = []

        for item in items:
            placed = False
            for cluster in clusters:
                if self.detector.is_duplicate(cluster[0].content, item.content):
                    cluster.append(item)
                    placed = True
                    break
            if not placed:
                clusters.append([item])

        return clusters
