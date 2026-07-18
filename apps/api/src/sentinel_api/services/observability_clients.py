import structlog
import httpx
from typing import Dict, Any, List, Optional
import datetime

logger = structlog.get_logger("sentinel_api.services.observability_clients")

class BaseObservabilityClient:
    def __init__(self, base_url: str, auth_method: str = "none", credentials: Dict[str, Any] = None):
        self.base_url = base_url.rstrip("/")
        self.auth_method = auth_method
        self.credentials = credentials or {}
        
        self.headers = {"Accept": "application/json"}
        
        if self.auth_method == "bearer":
            token = self.credentials.get("token", "")
            self.headers["Authorization"] = f"Bearer {token}"
        elif self.auth_method == "basic":
            import base64
            username = self.credentials.get("username", "")
            password = self.credentials.get("password", "")
            encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
            self.headers["Authorization"] = f"Basic {encoded}"

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}{path}"
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

class PrometheusClient(BaseObservabilityClient):
    """Client for querying Prometheus metrics and fetching rules."""
    
    async def query(self, query: str) -> Dict[str, Any]:
        """Execute a PromQL query."""
        return await self._get("/api/v1/query", params={"query": query})
        
    async def get_rules(self) -> Dict[str, Any]:
        """Fetch all recording and alerting rules."""
        return await self._get("/api/v1/rules")

class GrafanaClient(BaseObservabilityClient):
    """Client for querying Grafana dashboards and folders."""
    
    async def search_dashboards(self) -> List[Dict[str, Any]]:
        """Search for all dashboards."""
        return await self._get("/api/search", params={"type": "dash-db"})
        
    async def get_dashboard(self, uid: str) -> Dict[str, Any]:
        """Get a specific dashboard by UID."""
        return await self._get(f"/api/dashboards/uid/{uid}")

class LokiClient(BaseObservabilityClient):
    """Client for querying Loki logs."""
    
    async def query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """Execute a LogQL query."""
        return await self._get("/loki/api/v1/query", params={"query": query, "limit": limit})

class AlertmanagerClient(BaseObservabilityClient):
    """Client for Alertmanager alerts and silences."""
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        return await self._get("/api/v2/alerts")
        
    async def get_silences(self) -> List[Dict[str, Any]]:
        return await self._get("/api/v2/silences")
