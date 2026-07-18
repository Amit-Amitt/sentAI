from datetime import UTC, datetime
import json
import re
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger("sentinel_api.ai.agents.log_agent.parser")

# Regular expression matching structured logs:
# e.g., 2026-07-17T23:40:28Z INFO service-name [ingress] : Message text
TIMESTAMP_PATTERN = (
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)"
)
LEVEL_PATTERN = r"(?P<level>INFO|WARN|WARNING|ERROR|CRITICAL|FATAL|DEBUG)"
SERVICE_PATTERN = r"(?P<service>[a-zA-Z0-9\-_]+)"
COMPONENT_PATTERN = r"(?:\[(?P<component>[a-zA-Z0-9\-_]+)\])?"

LOG_REGEX = re.compile(
    rf"^{TIMESTAMP_PATTERN}\s+{LEVEL_PATTERN}\s+{SERVICE_PATTERN}\s*{COMPONENT_PATTERN}?\s*:\s*(?P<message>.*)$",
    re.IGNORECASE,
)

FALLBACK_TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}")
FALLBACK_LEVEL = re.compile(
    r"\b(INFO|WARN|WARNING|ERROR|CRITICAL|FATAL|DEBUG)\b", re.IGNORECASE
)


class LogParser:
    """Parses log lines in JSON, structured, or plain text formats."""

    def parse_logs(self, raw_logs: str) -> List[Dict[str, Any]]:
        """Parses a newline-separated block of raw logs into standard dictionary mappings."""
        logger.info("Initializing log parsing execution")
        parsed_lines: List[Dict[str, Any]] = []
        lines = raw_logs.strip().split("\n")

        for line in lines:
            if not line.strip():
                continue
            parsed = self.parse_line(line)
            if parsed:
                parsed_lines.append(parsed)

        logger.info(
            "Log parsing completed",
            total_lines=len(lines),
            parsed_lines=len(parsed_lines),
        )
        return parsed_lines

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parses a single log line into a unified structure."""
        line = line.strip()

        # 1. Parse JSON log
        if line.startswith("{") and line.endswith("}"):
            try:
                data = json.loads(line)
                return self._format_json_log(data, line)
            except json.JSONDecodeError:
                pass

        # 2. Parse Structured Log using RegEx
        match = LOG_REGEX.match(line)
        if match:
            gd = match.groupdict()
            return {
                "timestamp": self._normalize_timestamp(gd.get("timestamp")),
                "level": gd.get("level", "INFO").upper(),
                "service": gd.get("service"),
                "component": gd.get("component"),
                "message": gd.get("message", "").strip(),
                "raw_line": line,
                "metadata": {},
            }

        # 3. Fallback for mixed or unstructured logs
        ts_match = FALLBACK_TIMESTAMP.search(line)
        lvl_match = FALLBACK_LEVEL.search(line)

        timestamp = (
            self._normalize_timestamp(ts_match.group(0))
            if ts_match
            else datetime.now(UTC).isoformat()
        )
        level = lvl_match.group(0).upper() if lvl_match else "INFO"

        # Clean message from timestamp/level markers
        message = line
        if ts_match:
            message = message.replace(ts_match.group(0), "")
        if lvl_match:
            message = message.replace(lvl_match.group(0), "")
        message = re.sub(r"\s+", " ", message).strip()

        return {
            "timestamp": timestamp,
            "level": level,
            "service": "unknown-service",
            "component": None,
            "message": message,
            "raw_line": line,
            "metadata": {},
        }

    def _format_json_log(
        self, data: Dict[str, Any], raw_line: str
    ) -> Dict[str, Any]:
        """Maps specific keys from a JSON dictionary log structure into standardized fields."""
        ts_keys = ["timestamp", "time", "@timestamp", "ts"]
        timestamp = next(
            (data[k] for k in ts_keys if k in data), datetime.now(UTC).isoformat()
        )

        lvl_keys = ["level", "lvl", "severity", "log_level"]
        level = next((data[k] for k in lvl_keys if k in data), "INFO")

        msg_keys = ["message", "msg", "log", "text"]
        message = next((data[k] for k in msg_keys if k in data), raw_line)

        service = data.get("service") or data.get("app") or "unknown-service"
        component = data.get("component") or data.get("module")

        standard_keys = ts_keys + lvl_keys + msg_keys + ["service", "app", "component", "module"]
        metadata = {k: v for k, v in data.items() if k not in standard_keys}

        return {
            "timestamp": self._normalize_timestamp(str(timestamp)),
            "level": str(level).upper(),
            "service": str(service),
            "component": str(component) if component else None,
            "message": str(message).strip(),
            "raw_line": raw_line,
            "metadata": metadata,
        }

    def _normalize_timestamp(self, ts_str: Optional[str]) -> str:
        """Standardizes timestamps to ISO 8601 UTC string."""
        if not ts_str:
            return datetime.now(UTC).isoformat()
        try:
            ts_str = ts_str.strip()
            if " " in ts_str and "T" not in ts_str:
                ts_str = ts_str.replace(" ", "T")
            if (
                not ts_str.endswith("Z")
                and "+" not in ts_str
                and "-" not in ts_str[-6:]
            ):
                ts_str += "Z"
            return ts_str
        except Exception:
            return datetime.now(UTC).isoformat()
