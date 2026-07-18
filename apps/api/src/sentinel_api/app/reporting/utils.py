from datetime import datetime, UTC


def get_current_utc_timestamp() -> str:
    """Generates the current ISO 8601 UTC timestamp."""
    return datetime.now(UTC).isoformat()


def format_timestamp_friendly(ts_str: str) -> str:
    """Converts ISO 8601 strings into a human-readable display string."""
    if not ts_str:
        return ""
    ts_str = ts_str.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        return ts_str
