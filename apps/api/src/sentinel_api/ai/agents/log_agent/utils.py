import re

HEX_PATTERN = re.compile(r"\b0x[a-fA-F0-9]+\b")
UUID_PATTERN = re.compile(
    r"\b[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\b"
)
IP_PATTERN = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
DIGITS_PATTERN = re.compile(r"\b\d+\b")
URL_PATTERN = re.compile(r"https?://\S+")
QUOTED_VALS_PATTERN = re.compile(r"(['\"])(.*?)\1")


def clean_log_message(msg: str) -> str:
    """Strips variable parameters (IPs, UUIDs, IDs, numbers) to form a comparison template."""
    msg = msg.strip()
    msg = URL_PATTERN.sub("<URL>", msg)
    msg = UUID_PATTERN.sub("<UUID>", msg)
    msg = HEX_PATTERN.sub("<HEX>", msg)
    msg = IP_PATTERN.sub("<IP>", msg)
    msg = QUOTED_VALS_PATTERN.sub(r"\1<VAL>\1", msg)
    msg = DIGITS_PATTERN.sub("<NUM>", msg)

    # Normalize whitespaces
    msg = re.sub(r"\s+", " ", msg)
    return msg.strip()
