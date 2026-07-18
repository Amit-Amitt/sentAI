import uuid
import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from sentinel_api.database.session import engine
from sentinel_api.models.observability import ObservabilityIntegration, GrafanaDashboard, PrometheusRule, AlertmanagerSilence
from sentinel_api.services.observability_clients import GrafanaClient, PrometheusClient

logger = structlog.get_logger("sentinel_api.workers.observability_tasks")

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def _sync_grafana_dashboards_async(integration_id: str):
    """Fetch Grafana dashboards and sync to database."""
    async with AsyncSessionLocal() as db:
        stmt = select(ObservabilityIntegration).where(
            ObservabilityIntegration.id == uuid.UUID(integration_id),
            ObservabilityIntegration.integration_type == "grafana"
        )
        result = await db.execute(stmt)
        integration = result.scalar_one_or_none()
        
        if not integration:
            logger.error("Grafana integration not found", integration_id=integration_id)
            return

        client = GrafanaClient(
            base_url=integration.url,
            auth_method=integration.auth_method,
            credentials=integration.credentials
        )
        
        try:
            dashboards = await client.search_dashboards()
            for dash in dashboards:
                uid = dash.get("uid")
                
                # Fetch full dashboard details for tags/panels
                dash_detail = await client.get_dashboard(uid)
                dashboard_data = dash_detail.get("dashboard", {})
                
                stmt_dash = select(GrafanaDashboard).where(
                    GrafanaDashboard.integration_id == integration.id,
                    GrafanaDashboard.uid == uid
                )
                res_dash = await db.execute(stmt_dash)
                existing = res_dash.scalar_one_or_none()
                
                if existing:
                    existing.title = dash.get("title")
                    existing.url = f"{integration.url}{dash.get('url')}"
                    existing.folder_title = dash.get("folderTitle")
                    existing.tags = dashboard_data.get("tags", [])
                else:
                    db.add(GrafanaDashboard(
                        id=uuid.uuid4(),
                        integration_id=integration.id,
                        uid=uid,
                        title=dash.get("title"),
                        url=f"{integration.url}{dash.get('url')}",
                        folder_title=dash.get("folderTitle"),
                        tags=dashboard_data.get("tags", []),
                        panels=[] # Complex extraction in real scenarios
                    ))
            
            integration.last_synced_at = datetime.datetime.utcnow()
            await db.commit()
        except Exception as e:
            logger.error("Failed to sync Grafana dashboards", error=str(e))


async def _sync_prometheus_rules_async(integration_id: str):
    """Fetch Prometheus recording and alert rules."""
    async with AsyncSessionLocal() as db:
        stmt = select(ObservabilityIntegration).where(
            ObservabilityIntegration.id == uuid.UUID(integration_id),
            ObservabilityIntegration.integration_type == "prometheus"
        )
        result = await db.execute(stmt)
        integration = result.scalar_one_or_none()
        
        if not integration:
            logger.error("Prometheus integration not found", integration_id=integration_id)
            return

        client = PrometheusClient(
            base_url=integration.url,
            auth_method=integration.auth_method,
            credentials=integration.credentials
        )
        
        try:
            rules_resp = await client.get_rules()
            groups = rules_resp.get("data", {}).get("groups", [])
            
            for group in groups:
                group_name = group.get("name")
                for rule in group.get("rules", []):
                    name = rule.get("name")
                    query = rule.get("query")
                    rule_type = rule.get("type", "unknown")
                    
                    stmt_rule = select(PrometheusRule).where(
                        PrometheusRule.integration_id == integration.id,
                        PrometheusRule.group_name == group_name,
                        PrometheusRule.name == name
                    )
                    res_rule = await db.execute(stmt_rule)
                    existing = res_rule.scalar_one_or_none()
                    
                    if existing:
                        existing.query = query
                        existing.duration = str(rule.get("duration"))
                        existing.labels = rule.get("labels", {})
                        existing.annotations = rule.get("annotations", {})
                    else:
                        db.add(PrometheusRule(
                            id=uuid.uuid4(),
                            integration_id=integration.id,
                            group_name=group_name,
                            name=name,
                            query=query,
                            duration=str(rule.get("duration")),
                            labels=rule.get("labels", {}),
                            annotations=rule.get("annotations", {}),
                            rule_type=rule_type
                        ))
                        
            integration.last_synced_at = datetime.datetime.utcnow()
            await db.commit()
        except Exception as e:
            logger.error("Failed to sync Prometheus rules", error=str(e))

def sync_grafana_dashboards(integration_id: str):
    import asyncio
    asyncio.run(_sync_grafana_dashboards_async(integration_id))

def sync_prometheus_rules(integration_id: str):
    import asyncio
    asyncio.run(_sync_prometheus_rules_async(integration_id))
