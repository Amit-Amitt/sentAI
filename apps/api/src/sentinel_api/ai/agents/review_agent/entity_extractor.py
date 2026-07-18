import re
from typing import Dict, List, Set
import structlog

logger = structlog.get_logger("sentinel_api.ai.agents.review_agent.entity_extractor")


class EntityExtractor:
    """Extracts endpoints, error strings, browsers, devices, and platforms."""

    def __init__(self) -> None:
        self.features = [
            "checkout page",
            "login button",
            "cart page",
            "invoice download",
            "search bar",
            "reset password",
            "profile settings",
        ]
        self.services = [
            "auth-service",
            "payment-service",
            "user-service",
            "cart-service",
            "api-gateway",
            "billing-worker",
        ]
        self.platforms = ["ios", "android", "windows", "macos", "linux"]
        self.browsers = ["chrome", "safari", "firefox", "edge"]
        self.devices = ["iphone", "pixel", "galaxy", "ipad", "macbook", "thinkpad"]

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Scans the text using regex and lexicons to isolate entities."""
        logger.debug("Running regex entity extraction")
        text_lower = text.lower()
        extracted: Dict[str, Set[str]] = {
            "features": set(),
            "services": set(),
            "endpoints": set(),
            "errors": set(),
            "platforms": set(),
            "browsers": set(),
            "devices": set(),
        }

        endpoints = re.findall(r"/[a-zA-Z0-9_\-\/]+", text)
        for ep in endpoints:
            if len(ep.split("/")) > 2:
                extracted["endpoints"].add(ep)

        error_matches = re.findall(
            r"(?:5\d\d|4\d\d)\b.*?(?:error|failed|refused|unauthorized|timeout)",
            text,
            re.IGNORECASE,
        )
        for err in error_matches:
            extracted["errors"].add(err.strip())

        for f in self.features:
            if f in text_lower:
                extracted["features"].add(f)

        for s in self.services:
            if s in text_lower:
                extracted["services"].add(s)

        platform_map = {
            "ios": "iOS",
            "android": "Android",
            "windows": "Windows",
            "macos": "macOS",
            "linux": "Linux",
        }
        for p in self.platforms:
            if p in text_lower:
                extracted["platforms"].add(platform_map.get(p, p.capitalize()))

        for b in self.browsers:
            if b in text_lower:
                extracted["browsers"].add(b.capitalize())

        for d in self.devices:
            if d in text_lower:
                extracted["devices"].add(d.capitalize())

        if "timeout" in text_lower:
            extracted["errors"].add("Timeout")
        if "connection refused" in text_lower:
            extracted["errors"].add("Connection Refused")

        return {k: sorted(list(v)) for k, v in extracted.items()}
