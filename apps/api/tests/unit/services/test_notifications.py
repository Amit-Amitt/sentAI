import pytest
import uuid
from typing import Any, Dict

from sentinel_api.services.notification_providers import get_provider, BaseProvider, SlackProvider, PagerDutyProvider

@pytest.mark.asyncio
async def test_get_provider_slack():
    config = {"webhook_url": "https://hooks.slack.com/services/..."}
    provider = get_provider("slack", config)
    
    assert isinstance(provider, SlackProvider)
    assert provider.config == config

@pytest.mark.asyncio
async def test_get_provider_pagerduty():
    config = {"routing_key": "1234567890"}
    provider = get_provider("pagerduty", config)
    
    assert isinstance(provider, PagerDutyProvider)
    assert provider.config == config

@pytest.mark.asyncio
async def test_get_provider_invalid():
    with pytest.raises(ValueError):
        get_provider("invalid_provider", {})

# For a full integration suite, we would use `respx` to mock `httpx` and verify the outgoing HTTP 
# requests match the required formatting for Slack Block Kit or PagerDuty Events API.
