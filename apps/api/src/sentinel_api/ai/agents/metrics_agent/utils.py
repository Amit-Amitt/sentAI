import math
from datetime import datetime, UTC
from typing import List


def parse_timestamp(ts_str: str) -> datetime:
    """Parses standard ISO 8601 string to datetime."""
    ts_str = ts_str.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(ts_str)
    except ValueError:
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                return datetime.strptime(ts_str, fmt).replace(tzinfo=UTC)
            except ValueError:
                pass
        return datetime.now(UTC)


def calculate_percentile(values: List[float], percentile: float) -> float:
    """Calculates percentile (0.0 to 1.0) on a list of numerical values."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * percentile
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    d0 = sorted_vals[int(f)] * (c - k)
    d1 = sorted_vals[int(c)] * (k - f)
    return d0 + d1


def calculate_std_dev(values: List[float], mean: float) -> float:
    """Calculates standard deviation on a list of values."""
    if len(values) < 2:
        return 0.0
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)
