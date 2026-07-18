from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.log_agent.schemas import LogSummary

logger = structlog.get_logger("sentinel_api.ai.agents.log_agent.summarizer")


class LogSummarizer:
    """Programmatically constructs standard incident narratives and contributor observations."""

    def summarize(
        self,
        findings: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        total_parsed: int,
    ) -> LogSummary:
        """Assembles the short/detailed summaries, observations, and contributing causes."""
        logger.info("Generating log analysis summaries")

        services_str = ", ".join(metadata.get("services", ["unknown"]))
        critical_count = sum(1 for f in findings if f.get("severity") == "Critical")
        high_count = sum(1 for f in findings if f.get("severity") == "High")

        # 1. Short Summary
        short_summary = (
            f"Log analysis completed on {total_parsed} log lines across "
            f"service(s) [{services_str}]. Detected {len(findings)} unique error patterns "
            f"({critical_count} Critical, {high_count} High)."
        )

        # 2. Detailed Summary
        anomalies_summary = ""
        if anomalies:
            anomalies_summary = f" {len(anomalies)} operational anomalies were flagged."

        detailed_summary = (
            "The log stream was analyzed for the presence of known error signatures, "
            f"high-frequency faults, and metadata correlations.{anomalies_summary} "
            f"The primary services identified are: {services_str}. "
            f"The errors spanned components: {', '.join(metadata.get('components', ['N/A'])) or 'N/A'}."
        )

        # 3. Key Observations
        key_observations: List[str] = []
        for anomaly in anomalies:
            key_observations.append(anomaly["description"])

        sorted_findings = sorted(
            findings, key=lambda x: x.get("occurrences", 0), reverse=True
        )
        for f in sorted_findings[:3]:
            template = f.get("template") or f.get("summary", "")
            key_observations.append(
                f"[{f['severity']}] Pattern '{template}' was observed"
                f" {f['occurrences']} times belonging to category {f['category']}."
            )

        if not key_observations:
            key_observations.append(
                "No errors or warnings of significant frequency or severity were"
                " observed."
            )

        # 4. Potential Contributors
        potential_contributors: List[str] = []
        categories = {f["category"] for f in findings}

        if "MEMORY" in categories:
            potential_contributors.append(
                "Application hit memory limits (OOM), suggesting potential leak or"
                " undersized instance size."
            )
        if "DISK" in categories:
            potential_contributors.append(
                "Host run out of disk space, leading to inability to log or write"
                " temporary assets."
            )
        if "CONNECTION" in categories:
            potential_contributors.append(
                "Database or peer network socket refused connection. Possible network"
                " partition or peer crash."
            )
        if "TIMEOUT" in categories:
            potential_contributors.append(
                "Upstream service or query execution exceeded timeout limit. Potential"
                " performance bottleneck."
            )
        if "AUTHENTICATION" in categories:
            potential_contributors.append(
                "Increased auth request rejections. Possible misconfiguration or"
                " security credential rotation failure."
            )
        if "HTTP_5XX" in categories:
            potential_contributors.append(
                "Web application returned HTTP 500 series failures. Possible unhandled"
                " application exception or crash."
            )

        if not potential_contributors:
            potential_contributors.append(
                "Normal operational bounds observed. No obvious infrastructure triggers"
                " detected."
            )

        return LogSummary(
            short_summary=short_summary,
            detailed_summary=detailed_summary,
            key_observations=key_observations,
            potential_contributors=potential_contributors,
        )
