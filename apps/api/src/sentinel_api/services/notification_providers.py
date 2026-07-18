import structlog
import httpx
from typing import Dict, Any

logger = structlog.get_logger("sentinel_api.services.notification_providers")

class BaseProvider:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def deliver(self, title: str, message: str, severity: str, context: Dict[str, Any] = None) -> bool:
        raise NotImplementedError

class SlackProvider(BaseProvider):
    async def deliver(self, title: str, message: str, severity: str, context: Dict[str, Any] = None) -> bool:
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return False
            
        color = "#ff0000" if severity in ["High", "Critical"] else "#ffcc00"
        
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": title,
                    "text": message,
                    "fields": [
                        {"title": "Severity", "value": severity, "short": True}
                    ]
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            res = await client.post(webhook_url, json=payload)
            res.raise_for_status()
            return True

class TeamsProvider(BaseProvider):
    async def deliver(self, title: str, message: str, severity: str, context: Dict[str, Any] = None) -> bool:
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return False
            
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "E81123" if severity in ["High", "Critical"] else "FFC107",
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "activitySubtitle": f"Severity: {severity}",
                "text": message
            }]
        }
        
        async with httpx.AsyncClient() as client:
            res = await client.post(webhook_url, json=payload)
            res.raise_for_status()
            return True

class PagerDutyProvider(BaseProvider):
    async def deliver(self, title: str, message: str, severity: str, context: Dict[str, Any] = None) -> bool:
        routing_key = self.config.get("routing_key")
        if not routing_key:
            return False
            
        payload = {
            "routing_key": routing_key,
            "event_action": "trigger",
            "payload": {
                "summary": title,
                "severity": "critical" if severity in ["High", "Critical"] else "warning",
                "source": "Sentinel AI",
                "custom_details": {
                    "description": message
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            res = await client.post("https://events.pagerduty.com/v2/enqueue", json=payload)
            res.raise_for_status()
            return True

class DiscordProvider(BaseProvider):
    async def deliver(self, title: str, message: str, severity: str, context: Dict[str, Any] = None) -> bool:
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return False
            
        payload = {
            "embeds": [{
                "title": title,
                "description": message,
                "color": 16711680 if severity in ["High", "Critical"] else 16776960
            }]
        }
        
        async with httpx.AsyncClient() as client:
            res = await client.post(webhook_url, json=payload)
            res.raise_for_status()
            return True

class EmailProvider(BaseProvider):
    async def deliver(self, title: str, message: str, severity: str, context: Dict[str, Any] = None) -> bool:
        api_key = self.config.get("resend_api_key")
        to_email = self.config.get("to_email")
        if not api_key or not to_email:
            return False
            
        payload = {
            "from": "Sentinel AI <alerts@sentinel-ai.com>",
            "to": [to_email],
            "subject": f"[{severity.upper()}] {title}",
            "html": f"<h2>{title}</h2><p><strong>Severity:</strong> {severity}</p><p>{message}</p>"
        }
        
        headers = {"Authorization": f"Bearer {api_key}"}
        
        async with httpx.AsyncClient() as client:
            res = await client.post("https://api.resend.com/emails", json=payload, headers=headers)
            res.raise_for_status()
            return True

def get_provider(provider_type: str, config: Dict[str, Any]) -> BaseProvider:
    providers = {
        "slack": SlackProvider,
        "teams": TeamsProvider,
        "pagerduty": PagerDutyProvider,
        "discord": DiscordProvider,
        "email": EmailProvider
    }
    provider_cls = providers.get(provider_type)
    if not provider_cls:
        raise ValueError(f"Unknown provider type: {provider_type}")
    return provider_cls(config)
