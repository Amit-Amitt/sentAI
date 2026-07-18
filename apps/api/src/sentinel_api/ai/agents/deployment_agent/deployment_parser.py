import json
from datetime import datetime, UTC
from typing import Any, List
import structlog

from sentinel_api.ai.agents.deployment_agent.schemas import DeploymentEvent

logger = structlog.get_logger("sentinel_api.ai.agents.deployment_agent.deployment_parser")


class DeploymentParser:
    """Parses raw deployment feeds, commit details, config mappings into DeploymentEvents."""

    def parse(self, raw_data: Any) -> List[DeploymentEvent]:
        """Triages the raw payload into a standard list of DeploymentEvents."""
        logger.info("Triage deployment payload input")
        events: List[DeploymentEvent] = []

        if not raw_data:
            return events

        if isinstance(raw_data, str):
            raw_str = raw_data.strip()
            if not raw_str:
                return events
            try:
                raw_data = json.loads(raw_str)
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON deployment raw data")
                return events

        if isinstance(raw_data, dict):
            for key in ["deployments", "releases", "events", "history", "changes"]:
                if key in raw_data and isinstance(raw_data[key], list):
                    return self.parse(raw_data[key])
            single = self._parse_single(raw_data)
            if single:
                events.append(single)
            return events

        if isinstance(raw_data, list):
            for item in raw_data:
                single = self._parse_single(item)
                if single:
                    events.append(single)
            return events

        return events

    def _parse_single(self, item: Any) -> DeploymentEvent | None:
        """Translates a raw log dictionary into a DeploymentEvent model."""
        if not isinstance(item, dict):
            return None

        dep_id = (
            item.get("deployment_id")
            or item.get("id")
            or item.get("release_id")
            or item.get("commit_sha")
            or "dep-unknown"
        )

        service = (
            item.get("service")
            or item.get("service_name")
            or item.get("app")
            or item.get("application")
            or "unknown-service"
        )

        version = (
            item.get("version")
            or item.get("commit_sha")
            or item.get("image_tag")
            or item.get("ref")
            or "v1.0.0"
        )

        env = (
            item.get("environment")
            or item.get("env")
            or item.get("target_env")
            or "prod"
        )

        ts = (
            item.get("timestamp")
            or item.get("created_at")
            or item.get("deployed_at")
            or datetime.now(UTC).isoformat()
        )

        change_type = item.get("change_type") or item.get("type") or "APP"
        change_type = change_type.upper()
        if change_type not in ["APP", "CONFIG", "FLAG", "INFRA", "DB"]:
            change_type_lower = change_type.lower()
            if (
                "flag" in change_type_lower
                or "toggle" in change_type_lower
                or "feature" in change_type_lower
            ):
                change_type = "FLAG"
            elif (
                "config" in change_type_lower
                or "env" in change_type_lower
                or "secret" in change_type_lower
            ):
                change_type = "CONFIG"
            elif (
                "infra" in change_type_lower
                or "terraform" in change_type_lower
                or "k8s" in change_type_lower
                or "kubernetes" in change_type_lower
            ):
                change_type = "INFRA"
            elif (
                "db" in change_type_lower
                or "migration" in change_type_lower
                or "sql" in change_type_lower
            ):
                change_type = "DB"
            else:
                change_type = "APP"

        status_raw = item.get("status") or item.get("state") or item.get("outcome") or "SUCCESS"
        status_lower = status_raw.lower()
        if "fail" in status_lower or "error" in status_lower:
            status = "FAILED"
        elif "rollback" in status_lower or "revert" in status_lower:
            status = "ROLLBACK"
        else:
            status = "SUCCESS"

        details = {}
        for k, v in item.items():
            if k not in [
                "deployment_id",
                "id",
                "release_id",
                "service",
                "service_name",
                "app",
                "application",
                "version",
                "commit_sha",
                "image_tag",
                "ref",
                "environment",
                "env",
                "target_env",
                "timestamp",
                "created_at",
                "deployed_at",
                "change_type",
                "type",
                "status",
                "state",
                "outcome",
            ]:
                details[k] = v

        return DeploymentEvent(
            deployment_id=str(dep_id),
            service=str(service),
            version=str(version),
            environment=str(env),
            timestamp=str(ts),
            change_type=change_type,
            status=status,
            details=details,
        )
