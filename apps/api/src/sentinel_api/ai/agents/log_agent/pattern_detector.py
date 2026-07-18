import re
from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.log_agent.utils import clean_log_message

logger = structlog.get_logger("sentinel_api.ai.agents.log_agent.pattern_detector")

CATEGORIES = {
    "HTTP_5XX": [
        r"\b5\d\d\b",
        r"bad gateway",
        r"service unavailable",
        r"internal server error",
        r"502 bad gateway",
    ],
    "HTTP_4XX": [
        r"\b4\d\d\b",
        r"not found",
        r"unauthorized",
        r"forbidden",
        r"bad request",
        r"404 not found",
    ],
    "TIMEOUT": [r"timeout", r"timed out", r"deadline exceeded", r"gateway timeout"],
    "CONNECTION": [
        r"connection refused",
        r"cannot connect",
        r"failed to connect",
        r"connection reset",
        r"db connection",
    ],
    "AUTHENTICATION": [
        r"login failed",
        r"invalid token",
        r"auth error",
        r"permission denied",
        r"unauthorized",
    ],
    "MEMORY": [
        r"out of memory",
        r"oom",
        r"memory exhausted",
        r"heap limit",
        r"java\.lang\.OutOfMemoryError",
    ],
    "DISK": [r"no space left", r"disk full", r"write error", r"disk exhaustion"],
    "EXCEPTION": [
        r"traceback",
        r"exception",
        r"uncaught",
        r"nullpointerexception",
        r"stacktrace",
    ],
}


class PatternDetector:
    """Groups recurring error logs into templates and assigns incident categories."""

    def detect_patterns(
        self, parsed_logs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Clusters similar warning/error messages into findings with occurrance metrics."""
        logger.info("Starting log pattern detection")

        clusters: Dict[str, List[Dict[str, Any]]] = {}

        for log in parsed_logs:
            level = log.get("level", "INFO")
            msg = log.get("message", "")

            # We process warnings, debug traces, and errors for pattern clustering
            if level in ["WARN", "WARNING", "ERROR", "CRITICAL", "FATAL", "DEBUG"]:
                template = clean_log_message(msg)
                if template not in clusters:
                    clusters[template] = []
                clusters[template].append(log)

        findings = []
        for template, group in clusters.items():
            first = group[0]
            category = self._determine_category(template, group)

            timestamps = [g["timestamp"] for g in group]
            timestamps.sort()

            findings.append(
                {
                    "template": template,
                    "category": category,
                    "occurrences": len(group),
                    "sample_log": first["raw_line"],
                    "timestamp_start": timestamps[0],
                    "timestamp_end": timestamps[-1],
                    "level": first["level"],
                    "group_logs": group,
                }
            )

        logger.info(
            "Pattern detection completed", total_error_clusters=len(findings)
        )
        return findings

    def _determine_category(
        self, template: str, group: List[Dict[str, Any]]
    ) -> str:
        """Heuristically labels the log cluster with a standard categorization tag."""
        combined_text = (
            template + " " + " ".join(g["message"] for g in group)
        ).lower()

        for category, patterns in CATEGORIES.items():
            for pattern in patterns:
                if re.search(pattern, combined_text):
                    return category

        # Mark generic warnings or generic errors if log levels match
        for g in group:
            if g.get("level") in ["ERROR", "CRITICAL", "FATAL"]:
                return "GENERIC_ERROR"

        return "GENERIC_WARN"
