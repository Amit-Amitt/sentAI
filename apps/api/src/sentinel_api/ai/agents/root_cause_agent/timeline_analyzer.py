from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.root_cause_agent.utils import parse_timestamp

logger = structlog.get_logger(
    "sentinel_api.ai.agents.root_cause_agent.timeline_analyzer"
)


class TimelineAnalyzer:
    """Analyzes chronological events to structure cause-and-effect relationship paths."""

    def build_cause_effect_timeline(
        self, normalized_evidence: List[Dict[str, Any]]
    ) -> List[str]:
        """Traces sequential dependencies between deployments, anomalies, errors, and tickets."""
        logger.info("Analyzing chronological dependencies")

        sorted_ev = sorted(
            [e for e in normalized_evidence if e["timestamp"]],
            key=lambda x: parse_timestamp(x["timestamp"]),
        )

        steps: List[str] = []
        for idx, ev in enumerate(sorted_ev):
            t_str = parse_timestamp(ev["timestamp"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            desc = ev["description"]
            agent = ev["agent"]

            step = f"[{t_str}] {agent}: {desc}"
            if idx > 0:
                prev_agent = sorted_ev[idx - 1]["agent"]
                if prev_agent == "DEPLOYMENT" and agent in ["LOG", "METRICS"]:
                    step += " (Likely triggered by preceding deployment)"
                elif prev_agent in ["LOG", "METRICS"] and agent == "REVIEW":
                    step += " (Likely led to user reports and support volume)"
            steps.append(step)

        return steps
