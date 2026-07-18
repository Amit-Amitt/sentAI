import uuid
import datetime
import structlog
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.database.session import AsyncSessionLocal
from sentinel_api.models.telemetry import TelemetryEvent, TelemetryLog, TelemetryMetric, TelemetryException, TelemetryHealth
from sentinel_api.models.incident import Incident, DetectionRule, IncidentTimeline, IncidentEvidence, AffectedService, DetectionHistory
from sentinel_api.models.github import GithubDeployment, GithubCommit
from sentinel_api.models.kubernetes import K8sPod, K8sContainer, K8sEvent
from sentinel_api.models.observability import ObservabilityIntegration, GrafanaDashboard
from sentinel_api.services.integration_trigger import IntegrationTriggerService

logger = structlog.get_logger("sentinel_api.services.detection")

class TelemetryNormalizer:
    """Normalizes raw telemetry into a standardized format for rule evaluation."""
    @staticmethod
    def normalize(payload_type: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for item in data:
            if payload_type == "metrics":
                normalized.append({
                    "type": "metric",
                    "metric_name": item.get("name"),
                    "value": item.get("value"),
                    "timestamp": item.get("timestamp"),
                    "raw": item
                })
            elif payload_type in ["logs", "exceptions", "events", "spans"]:
                # If it's a span, extract trace_id for correlation
                trace_id = item.get("trace_id")
                
                normalized.append({
                    "type": "event",
                    "event_type": payload_type,
                    "level": item.get("level", item.get("status_code", item.get("type", "error"))),
                    "message": item.get("message", item.get("name", "")),
                    "timestamp": item.get("timestamp", item.get("start_time")),
                    "trace_id": trace_id,
                    "raw": item
                })
        return normalized

class AnomalyDetector:
    """Core anomaly detection algorithms."""
    @staticmethod
    def is_anomalous_zscore(values: List[float], current_value: float, threshold: float = 3.0) -> bool:
        if not values:
            return False
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        if std_dev == 0:
            return False
        z_score = abs((current_value - mean) / std_dev)
        return z_score > threshold

    @staticmethod
    def moving_average_deviation(values: List[float], current_value: float, deviation_pct: float = 0.5) -> bool:
        if not values:
            return False
        mean = sum(values) / len(values)
        if mean == 0:
            return current_value > 0
        diff = abs(current_value - mean) / mean
        return diff > deviation_pct

class SeverityEngine:
    """Calculates severity dynamically based on rule and context."""
    @staticmethod
    def calculate_severity(rule: DetectionRule, value: float) -> str:
        # Basic mapping, could be expanded to ML based
        base = rule.severity
        
        # Escalate severity if the threshold is vastly exceeded
        if rule.operator in [">", ">="] and rule.threshold:
            if value > rule.threshold * 5:
                return "Critical"
            elif value > rule.threshold * 2:
                if base in ["Info", "Low"]:
                    return "Medium"
                elif base == "Medium":
                    return "High"
        
        return base

class IncidentCorrelator:
    """Prevents duplicate incidents by correlating related events."""
    @staticmethod
    async def get_or_create_incident(
        db: AsyncSession, 
        project_id: uuid.UUID, 
        workspace_id: uuid.UUID, 
        rule: DetectionRule,
        severity: str,
        evidence: Dict[str, Any]
    ) -> Incident:
        
        # Deduplication fingerprint: Project + Rule ID
        fingerprint = f"{project_id}_{rule.id}"
        
        # Look for open incidents with same fingerprint
        stmt = select(Incident).where(
            Incident.fingerprint == fingerprint,
            Incident.status.in_(["Open", "Investigating", "AI Processing"])
        ).order_by(desc(Incident.created_at))
        
        result = await db.execute(stmt)
        existing_incident = result.scalar_one_or_none()
        
        if existing_incident:
            logger.info("Correlated anomaly to existing incident", incident_id=str(existing_incident.id))
            
            # If severity escalated, update it
            severity_levels = {"Info": 1, "Low": 2, "Medium": 3, "High": 4, "Critical": 5}
            if severity_levels.get(severity, 0) > severity_levels.get(existing_incident.severity, 0):
                timeline = IncidentTimeline(
                    incident_id=existing_incident.id,
                    action="severity_change",
                    previous_value=existing_incident.severity,
                    new_value=severity,
                    metadata_json={"rule": str(rule.id)}
                )
                db.add(timeline)
                existing_incident.severity = severity
            
            # Add new evidence
            new_evidence = IncidentEvidence(
                incident_id=existing_incident.id,
                evidence_type="RuleTrigger",
                payload=evidence
            )
            db.add(new_evidence)
            
            return existing_incident
        
        # Create new incident
        incident_key = f"INC-{project_id.hex[:4]}-{int(datetime.datetime.utcnow().timestamp())}"
        new_incident = Incident(
            project_id=project_id,
            workspace_id=workspace_id,
            incident_key=incident_key,
            status="Open",
            severity=severity,
            title=f"Anomaly Detected: {rule.name}",
            summary=f"Rule '{rule.name}' triggered. Target: {rule.target_metric} {rule.operator} {rule.threshold}",
            fingerprint=fingerprint,
            trigger_rule_id=rule.id
        )
        db.add(new_incident)
        await db.flush() # To get ID
        
        # Add initial timeline
        db.add(IncidentTimeline(
            incident_id=new_incident.id,
            action="status_change",
            new_value="Open",
            metadata_json={"reason": "Created by Rule Engine"}
        ))
        
        # Add evidence
        # Fetch the latest deployment for correlation
        latest_dep_stmt = select(GithubDeployment).where(
            GithubDeployment.project_id == project_id,
            GithubDeployment.status == "success",
            GithubDeployment.deployed_at <= datetime.datetime.utcnow()
        ).order_by(desc(GithubDeployment.deployed_at)).limit(1)
        
        dep_res = await db.execute(latest_dep_stmt)
        latest_deployment = dep_res.scalar_one_or_none()
        
        if latest_deployment:
            evidence["latest_deployment"] = {
                "deployment_id": latest_deployment.deployment_id,
                "commit_sha": latest_deployment.commit_sha,
                "deployed_at": latest_deployment.deployed_at.isoformat(),
                "author": latest_deployment.author_login,
                "risk_score": latest_deployment.risk_score,
                "risk_factors": latest_deployment.risk_factors
            }
            
        # Fetch Kubernetes correlation data if applicable
        pod_name = evidence.get("k8s.pod.name")
        namespace = evidence.get("k8s.namespace.name")
        
        if pod_name and namespace:
            stmt_pod = select(K8sPod).where(
                K8sPod.name == pod_name,
                K8sPod.namespace == namespace
            ).order_by(desc(K8sPod.created_at)).limit(1)
            
            res_pod = await db.execute(stmt_pod)
            pod = res_pod.scalar_one_or_none()
            
            if pod:
                evidence["kubernetes_context"] = {
                    "pod_name": pod.name,
                    "namespace": pod.namespace,
                    "node_name": pod.node_name,
                    "phase": pod.phase,
                    "status_message": pod.status_message,
                }
                
                # Fetch recent events for this pod
                stmt_events = select(K8sEvent).where(
                    K8sEvent.involved_object_name == pod.name,
                    K8sEvent.namespace == pod.namespace,
                    K8sEvent.event_type == "Warning"
                ).order_by(desc(K8sEvent.last_timestamp)).limit(5)
                
                res_events = await db.execute(stmt_events)
                events = res_events.scalars().all()
                if events:
                    evidence["kubernetes_context"]["recent_warnings"] = [
                        {"reason": e.reason, "message": e.message, "count": e.count} for e in events
                    ]

        # Fetch Grafana Dashboards for fast correlation links
        # For a production system we would match based on tags, labels or namespace.
        # Here we just fetch the top 3 synced dashboards for the project.
        stmt_dashboards = select(GrafanaDashboard).join(
            ObservabilityIntegration, GrafanaDashboard.integration_id == ObservabilityIntegration.id
        ).where(
            ObservabilityIntegration.project_id == project_id,
            ObservabilityIntegration.integration_type == "grafana"
        ).limit(3)
        
        res_dash = await db.execute(stmt_dashboards)
        dashboards = res_dash.scalars().all()
        if dashboards:
            evidence["observability_context"] = {
                "grafana_dashboards": [
                    {"title": d.title, "url": d.url, "tags": d.tags} for d in dashboards
                ]
            }

        db.add(IncidentEvidence(
            incident_id=new_incident.id,
            evidence_type="RuleTrigger",
            payload=evidence
        ))
        
        return new_incident

class RuleEngine:
    @staticmethod
    async def evaluate_static_rule(db: AsyncSession, rule: DetectionRule, project_id: uuid.UUID) -> Optional[float]:
        """Evaluates a static threshold rule against the DB within the time window."""
        window_start = datetime.datetime.utcnow() - datetime.timedelta(minutes=rule.time_window_mins)
        
        # This is a simplified engine that supports count of errors or average of a metric
        if "rate" in rule.target_metric or "error" in rule.target_metric:
            stmt = select(func.count(TelemetryEvent.id)).where(
                TelemetryEvent.project_id == project_id,
                TelemetryEvent.event_type.in_(["EXCEPTION", "ERROR", "500"]),
                TelemetryEvent.timestamp >= window_start
            )
            result = await db.execute(stmt)
            count = result.scalar() or 0
            
            if rule.operator == ">" and count > rule.threshold:
                return float(count)
            elif rule.operator == ">=" and count >= rule.threshold:
                return float(count)
                
        elif rule.target_metric == "latency":
            # Example metric rule
            stmt = select(func.avg(TelemetryMetric.value)).where(
                TelemetryMetric.project_id == project_id,
                TelemetryMetric.name == "latency",
                TelemetryMetric.timestamp >= window_start
            )
            result = await db.execute(stmt)
            avg_latency = result.scalar() or 0.0
            
            if rule.operator == ">" and avg_latency > rule.threshold:
                return float(avg_latency)
                
        return None

class DetectionEngine:
    @staticmethod
    async def evaluate_telemetry(project_id: str, workspace_id: str, payload_type: str, data: List[Dict[str, Any]]):
        """Main entrypoint from the ingestion worker."""
        
        # 1. Normalize telemetry
        normalized_data = TelemetryNormalizer.normalize(payload_type, data)
        if not normalized_data:
            return
            
        proj_uuid = uuid.UUID(project_id)
        workspace_uuid = uuid.UUID(workspace_id)
        
        async with AsyncSessionLocal() as db:
            # 2. Fetch active rules
            stmt = select(DetectionRule).where(
                DetectionRule.project_id == proj_uuid,
                DetectionRule.is_active == True
            )
            rules_result = await db.execute(stmt)
            active_rules = rules_result.scalars().all()
            
            # If no rules exist, apply a default fallback rule
            if not active_rules:
                default_rule = DetectionRule(
                    project_id=proj_uuid,
                    workspace_id=workspace_uuid,
                    name="High Error Rate Default",
                    condition_type="static_threshold",
                    target_metric="error_rate",
                    operator=">",
                    threshold=10,
                    time_window_mins=5,
                    severity="High"
                )
                active_rules = [default_rule]

            new_incidents = []

            # 3. Evaluate Rules
            for rule in active_rules:
                trigger_value = None
                
                if rule.condition_type == "static_threshold":
                    trigger_value = await RuleEngine.evaluate_static_rule(db, rule, proj_uuid)
                
                # 4. If triggered, handle correlation and incident creation
                if trigger_value is not None:
                    # Severity
                    calc_severity = SeverityEngine.calculate_severity(rule, trigger_value)
                    
                    # Collect associated trace IDs from the batch
                    associated_traces = list({item.get("trace_id") for item in normalized_data if item.get("trace_id")})
                    
                    # Extract k8s metadata from the first triggered item if available
                    k8s_pod = None
                    k8s_ns = None
                    for item in normalized_data:
                        raw = item.get("raw", {})
                        res_attrs = raw.get("resource_attributes", {})
                        if res_attrs.get("k8s.pod.name"):
                            k8s_pod = res_attrs.get("k8s.pod.name")
                            k8s_ns = res_attrs.get("k8s.namespace.name")
                            break
                    
                    evidence = {
                        "metric": rule.target_metric,
                        "value": trigger_value,
                        "threshold": rule.threshold,
                        "time_window": rule.time_window_mins,
                        "associated_traces": associated_traces,
                        "k8s.pod.name": k8s_pod,
                        "k8s.namespace.name": k8s_ns
                    }
                    
                    # History
                    if rule.id:
                        db.add(DetectionHistory(
                            project_id=proj_uuid,
                            rule_id=rule.id,
                            metric_value=trigger_value,
                            is_anomaly=True,
                            metadata_json=evidence
                        ))
                    
                    # Correlate
                    incident = await IncidentCorrelator.get_or_create_incident(
                        db, proj_uuid, workspace_uuid, rule, calc_severity, evidence
                    )
                    
                    if incident not in new_incidents:
                        new_incidents.append(incident)

            await db.commit()
            
            # 5. Trigger LangGraph via Integration Trigger Service
            for incident in new_incidents:
                # Refresh object to ensure ID is populated
                await db.refresh(incident)
                asyncio.create_task(
                    IntegrationTriggerService.trigger_workflow(str(incident.id), project_id, workspace_id)
                )

