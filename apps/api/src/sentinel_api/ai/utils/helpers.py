import json
import re
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


def count_tokens(text: str) -> int:
    """Heuristically estimates token counts for text inputs/outputs (approx. 4 chars per token)."""
    if not text:
        return 0
    words = text.split()
    word_estimate = int(len(words) * 1.33)
    char_estimate = len(text) // 4
    return max(word_estimate, char_estimate, 1)


class CustomJSONEncoder(json.JSONEncoder):
    """JSON Encoder that formats datetimes, UUIDs, and Pydantic models."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)


def serialize_json(data: Any) -> str:
    """Converts variables into formatted JSON string using CustomJSONEncoder."""
    return json.dumps(data, cls=CustomJSONEncoder)


def extract_and_parse_json(text: str) -> Any:
    """Extracts JSON substrings or markdown JSON blocks from LLM output, parsing them into python structures."""
    if not text:
        raise ValueError("Cannot parse empty text block.")

    # Match block pattern ```json <payload> ```
    json_block_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if json_block_match:
        target_text = json_block_match.group(1)
    else:
        target_text = text.strip()

    try:
        return json.loads(target_text)
    except json.JSONDecodeError as e:
        # Fallback to search for enclosing brackets
        bounds_match = re.search(r"(\{.*\}|\[.*\])", target_text, re.DOTALL)
        if bounds_match:
            try:
                return json.loads(bounds_match.group(1))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Failed to decode block into JSON: {e}") from e
