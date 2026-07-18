import re
from typing import Any, Dict, List, Set
import structlog

logger = structlog.get_logger("sentinel_api.ai.agents.log_agent.extractor")

REQUEST_ID_PATTERN = re.compile(
    r"\b(?:request_id|req_id|trace_id|req\-id|trace\-id)[:\s=]+([a-zA-Z0-9\-_]+)",
    re.IGNORECASE,
)
USER_ID_PATTERN = re.compile(
    r"\b(?:user_id|user\-id|uid)[:\s=]+([a-zA-Z0-9\-_@\.]+)", re.IGNORECASE
)
CORRELATION_ID_PATTERN = re.compile(
    r"\b(?:correlation_id|corr_id|correlation\-id)[:\s=]+([a-zA-Z0-9\-_]+)",
    re.IGNORECASE,
)
HOST_PATTERN = re.compile(
    r"\b(?:host|hostname)[:\s=]+([a-zA-Z0-9\.\-_]+)", re.IGNORECASE
)


class MetadataExtractor:
    """Scans and extracts identifiers and metadata context from parsed log lines."""

    def extract_metadata(
        self, parsed_logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregates environments, hosts, services, and tracing IDs across all log entries."""
        logger.info("Extracting log telemetry metadata")

        services: Set[str] = set()
        components: Set[str] = set()
        hosts: Set[str] = set()
        environments: Set[str] = set()
        request_ids: Set[str] = set()
        user_ids: Set[str] = set()
        correlation_ids: Set[str] = set()

        for log in parsed_logs:
            # 1. Extract from standard fields
            if log.get("service") and log["service"] != "unknown-service":
                services.add(log["service"])
                # Guess env from service name
                env_match = re.search(
                    r"\b(prod|staging|dev|sandbox|test)\b",
                    log["service"],
                    re.IGNORECASE,
                )
                if env_match:
                    environments.add(env_match.group(1).lower())

            if log.get("component"):
                components.add(log["component"])

            # 2. Extract from JSON metadata
            meta = log.get("metadata", {})
            if meta:
                for k in ["host", "hostname", "server"]:
                    if k in meta:
                        hosts.add(str(meta[k]))
                for k in ["env", "environment"]:
                    if k in meta:
                        environments.add(str(meta[k]).lower())
                for k in [
                    "request_id",
                    "req_id",
                    "trace_id",
                    "traceId",
                    "requestId",
                ]:
                    if k in meta:
                        request_ids.add(str(meta[k]))
                for k in ["user_id", "userId", "uid", "user"]:
                    if k in meta:
                        user_ids.add(str(meta[k]))
                for k in [
                    "correlation_id",
                    "correlationId",
                    "corrId",
                    "corr_id",
                ]:
                    if k in meta:
                        correlation_ids.add(str(meta[k]))

            # 3. Extract from raw messages via patterns
            msg = log.get("message", "")
            req = REQUEST_ID_PATTERN.search(msg)
            if req:
                request_ids.add(req.group(1))

            usr = USER_ID_PATTERN.search(msg)
            if usr:
                user_ids.add(usr.group(1))

            corr = CORRELATION_ID_PATTERN.search(msg)
            if corr:
                correlation_ids.add(corr.group(1))

            h_match = HOST_PATTERN.search(msg)
            if h_match:
                hosts.add(h_match.group(1))

        # Default fallback values
        if not environments:
            environments.add("production")

        return {
            "services": sorted(list(services)),
            "components": sorted(list(components)),
            "hosts": sorted(list(hosts)),
            "environments": sorted(list(environments)),
            "request_ids": sorted(list(request_ids)),
            "user_ids": sorted(list(user_ids)),
            "correlation_ids": sorted(list(correlation_ids)),
        }
