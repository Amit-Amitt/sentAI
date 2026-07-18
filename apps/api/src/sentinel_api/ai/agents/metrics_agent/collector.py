import json
import re
from datetime import datetime, UTC
from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.metrics_agent.schemas import MetricPoint

logger = structlog.get_logger("sentinel_api.ai.agents.metrics_agent.collector")

PROM_LINE_RE = re.compile(
    r"^(?P<name>[a-zA-Z_:][a-zA-Z0-9_:]*)(?:{(?P<labels>[^}]*)})?\s+(?P<value>[^\s]+)(?:\s+(?P<timestamp>\d+))?$"
)


class MetricsCollector:
    """Parses and normalizes multi-format metric feeds into standard MetricPoints."""

    def collect(self, raw_data: Any) -> List[MetricPoint]:
        """Triage and parse metrics payload from JSON lists, dicts, or Prometheus text."""
        logger.info("Collecting metrics payload")
        points: List[MetricPoint] = []

        if not raw_data:
            return points

        # Case 1: List of points
        if isinstance(raw_data, list):
            for item in raw_data:
                pt = self._parse_single_item(item)
                if pt:
                    points.append(pt)
            return points

        # Case 2: Dict format (e.g. {"metrics": [...]})
        if isinstance(raw_data, dict):
            for k in ["metrics", "data", "points"]:
                if k in raw_data and isinstance(raw_data[k], list):
                    return self.collect(raw_data[k])
            pt = self._parse_single_item(raw_data)
            if pt:
                points.append(pt)
            return points

        # Case 3: Raw string
        if isinstance(raw_data, str):
            raw_str = raw_data.strip()
            if not raw_str:
                return points

            if raw_str.startswith("[") or raw_str.startswith("{"):
                try:
                    parsed_json = json.loads(raw_str)
                    return self.collect(parsed_json)
                except json.JSONDecodeError:
                    pass

            return self._parse_prometheus(raw_str)

        return points

    def _parse_single_item(self, item: Any) -> MetricPoint | None:
        """Helper to transform a dictionary item into a MetricPoint."""
        if not isinstance(item, dict):
            return None

        name = item.get("name") or item.get("metric") or item.get("metric_name")
        if not name:
            return None

        val_raw = item.get("value")
        if val_raw is None:
            return None
        try:
            value = float(val_raw)
        except (ValueError, TypeError):
            return None

        ts_raw = item.get("timestamp") or item.get("time")
        if ts_raw:
            timestamp = str(ts_raw)
        else:
            timestamp = datetime.now(UTC).isoformat()

        labels = item.get("labels") or item.get("tags") or {}
        if not isinstance(labels, dict):
            labels = {}

        normalized_labels = {str(k): str(v) for k, v in labels.items()}

        return MetricPoint(
            name=str(name),
            value=value,
            timestamp=timestamp,
            labels=normalized_labels,
        )

    def _parse_prometheus(self, text: str) -> List[MetricPoint]:
        """Line-by-line Prometheus exposition parser."""
        points: List[MetricPoint] = []

        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            match = PROM_LINE_RE.match(line)
            if not match:
                continue

            name = match.group("name")
            val_str = match.group("value")
            labels_str = match.group("labels")
            ts_str = match.group("timestamp")

            try:
                value = float(val_str)
            except ValueError:
                continue

            labels = {}
            if labels_str:
                matches = re.finditer(
                    r'(?P<k>[a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*"(?P<v>[^"]*)"',
                    labels_str,
                )
                for m in matches:
                    labels[m.group("k")] = m.group("v")

            if ts_str:
                try:
                    ts_val = int(ts_str)
                    if ts_val > 9999999999:  # Epoch milliseconds
                        dt = datetime.fromtimestamp(ts_val / 1000.0, UTC)
                    else:
                        dt = datetime.fromtimestamp(ts_val, UTC)
                    timestamp = dt.isoformat()
                except (ValueError, TypeError):
                    timestamp = datetime.now(UTC).isoformat()
            else:
                timestamp = datetime.now(UTC).isoformat()

            points.append(
                MetricPoint(
                    name=name, value=value, timestamp=timestamp, labels=labels
                )
            )

        return points
