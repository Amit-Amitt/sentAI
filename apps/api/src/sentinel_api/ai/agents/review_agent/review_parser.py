import json
from datetime import datetime, UTC
from typing import Any, List
import structlog

from sentinel_api.ai.agents.review_agent.schemas import ReviewItem

logger = structlog.get_logger("sentinel_api.ai.agents.review_agent.review_parser")


class ReviewParser:
    """Parses raw Slack feeds, chat snippets, and emails into standardized ReviewItems."""

    def parse(self, raw_data: Any) -> List[ReviewItem]:
        """Triages the raw payload into a standard list of ReviewItems."""
        logger.info("Triaging raw feedback data streams")
        items: List[ReviewItem] = []

        if not raw_data:
            return items

        if isinstance(raw_data, str):
            raw_str = raw_data.strip()
            if not raw_str:
                return items
            try:
                raw_data = json.loads(raw_str)
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON feedback raw data")
                return items

        if isinstance(raw_data, dict):
            for key in [
                "tickets",
                "reviews",
                "feedback",
                "issues",
                "messages",
                "reports",
            ]:
                if key in raw_data and isinstance(raw_data[key], list):
                    return self.parse(raw_data[key])
            single = self._parse_single(raw_data)
            if single:
                items.append(single)
            return items

        if isinstance(raw_data, list):
            for item in raw_data:
                single = self._parse_single(item)
                if single:
                    items.append(single)
            return items

        return items

    def _parse_single(self, item: Any) -> ReviewItem | None:
        """Translates a raw dictionary block into a ReviewItem model."""
        if not isinstance(item, dict):
            return None

        item_id = (
            item.get("id")
            or item.get("ticket_id")
            or item.get("review_id")
            or item.get("issue_id")
            or item.get("msg_id")
            or f"rev-{hash(str(item))}"
        )

        source = (
            item.get("source")
            or item.get("channel")
            or item.get("type")
            or "Support Ticket"
        )

        content = (
            item.get("content")
            or item.get("text")
            or item.get("body")
            or item.get("message")
            or item.get("review")
            or item.get("description")
            or item.get("summary")
            or ""
        )

        ts = (
            item.get("timestamp")
            or item.get("created_at")
            or item.get("submitted_at")
            or datetime.now(UTC).isoformat()
        )

        details = {}
        for k, v in item.items():
            if k not in [
                "id",
                "ticket_id",
                "review_id",
                "issue_id",
                "msg_id",
                "source",
                "channel",
                "type",
                "content",
                "text",
                "body",
                "message",
                "review",
                "description",
                "summary",
                "timestamp",
                "created_at",
                "submitted_at",
            ]:
                details[k] = v

        return ReviewItem(
            id=str(item_id),
            source=str(source),
            content=str(content),
            timestamp=str(ts),
            details=details,
        )
