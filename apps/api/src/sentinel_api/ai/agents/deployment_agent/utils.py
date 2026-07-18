from datetime import datetime, UTC


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
