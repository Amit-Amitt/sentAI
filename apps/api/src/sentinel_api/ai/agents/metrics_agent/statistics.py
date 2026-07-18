from typing import Dict, List, Tuple
import structlog

from sentinel_api.ai.agents.metrics_agent.schemas import MetricPoint, MetricStats
from sentinel_api.ai.agents.metrics_agent.utils import (
    calculate_percentile,
    calculate_std_dev,
    parse_timestamp,
)

logger = structlog.get_logger("sentinel_api.ai.agents.metrics_agent.statistics")


class MetricStatsCalculator:
    """Computes basic statistics and rates of change for time-series streams."""

    def compute_stats(
        self,
        grouped_points: Dict[Tuple[str, frozenset], List[MetricPoint]],
    ) -> Dict[Tuple[str, frozenset], MetricStats]:
        """Calculates statistical profiles for each unique metric signature."""
        logger.info("Computing metrics time-series statistics")
        stats_dict = {}

        for key, points in grouped_points.items():
            if not points:
                continue

            sorted_pts = sorted(
                points, key=lambda x: parse_timestamp(x.timestamp)
            )
            values = [p.value for p in sorted_pts]

            mean = sum(values) / len(values)
            max_val = max(values)
            min_val = min(values)
            p95 = calculate_percentile(values, 0.95)
            std_dev = calculate_std_dev(values, mean)

            # Rate of change (delta per minute)
            rate = 0.0
            if len(sorted_pts) > 1:
                first = sorted_pts[0]
                last = sorted_pts[-1]
                t_first = parse_timestamp(first.timestamp)
                t_last = parse_timestamp(last.timestamp)
                dt_min = (t_last - t_first).total_seconds() / 60.0
                if dt_min > 0.01:
                    rate = (last.value - first.value) / dt_min

            stats_dict[key] = MetricStats(
                mean=round(mean, 3),
                max=round(max_val, 3),
                min=round(min_val, 3),
                p95=round(p95, 3),
                std_dev=round(std_dev, 3),
                rate_of_change=round(rate, 3),
            )

        return stats_dict
