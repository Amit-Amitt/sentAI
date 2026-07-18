import json
from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import BaseModel

from sentinel_api.ai.utils import count_tokens, extract_and_parse_json, serialize_json


class DummyModel(BaseModel):
    username: str
    active: bool


def test_token_counter():
    assert count_tokens("") == 0
    assert count_tokens("hello") == 1
    # Assert longer sentence returns positive count
    text = "Sentinel AI Platform utilizes structured workflows to analyze and triage incidents."
    assert count_tokens(text) > 4


def test_json_serializer():
    dt = datetime(2026, 7, 17, 10, 30, 0, tzinfo=UTC)
    uuid_val = UUID("12345678-1234-5678-1234-567812345678")
    model = DummyModel(username="admin", active=True)

    payload = {
        "time": dt,
        "uuid": uuid_val,
        "model": model,
        "number": 42,
    }

    raw = serialize_json(payload)
    parsed = json.loads(raw)

    assert parsed["time"] == "2026-07-17T10:30:00+00:00"
    assert parsed["uuid"] == "12345678-1234-5678-1234-567812345678"
    assert parsed["model"] == {"username": "admin", "active": True}
    assert parsed["number"] == 42


def test_json_parser_extractor():
    # Plain text
    assert extract_and_parse_json('{"key": "value"}') == {"key": "value"}

    # Markdown blocks
    md_payload = 'Output findings:\n```json\n{\n  "status": "completed"\n}\n```\nHope this helps.'
    assert extract_and_parse_json(md_payload) == {"status": "completed"}

    # Parsing crashes
    with pytest.raises(ValueError):
        extract_and_parse_json("This is definitely not a JSON payload")
