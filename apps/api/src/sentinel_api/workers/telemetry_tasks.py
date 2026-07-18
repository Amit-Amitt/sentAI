import json
import uuid
import asyncio
import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from sentinel_api.database.session import engine
from sentinel_api.models.telemetry import (
    TelemetryLog, TelemetryMetric, TelemetryEvent, 
    TelemetryException, TelemetryHeartbeat, TelemetryDeployment, TelemetryHealth
)
from sentinel_api.models.trace import Trace, Span, SpanEvent, SpanLink
from sentinel_api.services.telemetry_pipeline import redis_conn
from sentinel_api.services.detection import DetectionEngine

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def _process_telemetry_batch_async(payload_type: str, project_id: str, workspace_id: str, data: List[Dict[str, Any]]):
    events_to_insert = []
    
    # 1. Parse and map to domain models
    if payload_type == "logs":
        events_to_insert = [
            TelemetryLog(
                id=uuid.uuid4(),
                project_id=uuid.UUID(project_id),
                workspace_id=uuid.UUID(workspace_id),
                level=item.get("level"),
                message=item.get("message"),
                metadata_json=item.get("metadata", {}),
                timestamp=datetime.datetime.fromisoformat(item.get("timestamp").replace("Z", "+00:00")) if item.get("timestamp") else datetime.datetime.utcnow()
            ) for item in data
        ]
    elif payload_type == "metrics":
        events_to_insert = [
            TelemetryMetric(
                id=uuid.uuid4(),
                project_id=uuid.UUID(project_id),
                workspace_id=uuid.UUID(workspace_id),
                name=item.get("name"),
                value=item.get("value"),
                tags=item.get("tags", {}),
                timestamp=datetime.datetime.fromisoformat(item.get("timestamp").replace("Z", "+00:00")) if item.get("timestamp") else datetime.datetime.utcnow()
            ) for item in data
        ]
    elif payload_type == "events" or payload_type == "batch":
        events_to_insert = [
            TelemetryEvent(
                id=uuid.uuid4(),
                project_id=uuid.UUID(project_id),
                workspace_id=uuid.UUID(workspace_id),
                name=item.get("name", item.get("event_type", "EVENT")),
                payload=item.get("payload", item.get("data", {})),
                timestamp=datetime.datetime.fromisoformat(item.get("timestamp").replace("Z", "+00:00")) if item.get("timestamp") else datetime.datetime.utcnow()
            ) for item in data
        ]
    elif payload_type == "exceptions":
        events_to_insert = [
            TelemetryException(
                id=uuid.uuid4(),
                project_id=uuid.UUID(project_id),
                workspace_id=uuid.UUID(workspace_id),
                type=item.get("type", "Error"),
                message=item.get("message"),
                stack_trace=item.get("stack_trace"),
                tags=item.get("tags", {}),
                timestamp=datetime.datetime.fromisoformat(item.get("timestamp").replace("Z", "+00:00")) if item.get("timestamp") else datetime.datetime.utcnow()
            ) for item in data
        ]
    elif payload_type == "heartbeats":
        events_to_insert = [
            TelemetryHeartbeat(
                id=uuid.uuid4(),
                project_id=uuid.UUID(project_id),
                workspace_id=uuid.UUID(workspace_id),
                environment=item.get("environment", "unknown"),
                version=item.get("version"),
                cpu=item.get("cpu"),
                memory=item.get("memory"),
                health=item.get("health"),
                timestamp=datetime.datetime.fromisoformat(item.get("timestamp").replace("Z", "+00:00")) if item.get("timestamp") else datetime.datetime.utcnow()
            ) for item in data
        ]
    elif payload_type == "deployments":
        events_to_insert = [
            TelemetryDeployment(
                id=uuid.uuid4(),
                project_id=uuid.UUID(project_id),
                workspace_id=uuid.UUID(workspace_id),
                version=item.get("version"),
                environment=item.get("environment"),
                status=item.get("status"),
                metadata_json=item.get("metadata", {}),
                timestamp=datetime.datetime.fromisoformat(item.get("timestamp").replace("Z", "+00:00")) if item.get("timestamp") else datetime.datetime.utcnow()
            ) for item in data
        ]
    elif payload_type == "health":
        events_to_insert = [
            TelemetryHealth(
                id=uuid.uuid4(),
                project_id=uuid.UUID(project_id),
                workspace_id=uuid.UUID(workspace_id),
                service_name=item.get("service_name"),
                status=item.get("status"),
                latency_ms=item.get("latency_ms"),
                timestamp=datetime.datetime.fromisoformat(item.get("timestamp").replace("Z", "+00:00")) if item.get("timestamp") else datetime.datetime.utcnow()
            ) for item in data
        ]

    # For traces and spans
    traces_to_insert = {}
    spans_to_insert = []
    
    if payload_type == "spans":
        for item in data:
            trace_id = item.get("trace_id")
            if trace_id not in traces_to_insert:
                traces_to_insert[trace_id] = Trace(
                    id=uuid.uuid4(),
                    project_id=uuid.UUID(project_id),
                    workspace_id=uuid.UUID(workspace_id),
                    trace_id=trace_id,
                    root_span_id=item.get("span_id") if not item.get("parent_span_id") else None,
                    start_time=datetime.datetime.fromisoformat(item.get("start_time")),
                    has_errors=item.get("status_code") == "ERROR"
                )
            
            span_events = [
                SpanEvent(
                    id=uuid.uuid4(),
                    name=ev.get("name"),
                    timestamp=datetime.datetime.fromisoformat(ev.get("timestamp")),
                    attributes=ev.get("attributes", {})
                ) for ev in item.get("events", [])
            ]
            
            span_links = [
                SpanLink(
                    id=uuid.uuid4(),
                    linked_trace_id=lnk.get("linked_trace_id"),
                    linked_span_id=lnk.get("linked_span_id"),
                    attributes=lnk.get("attributes", {})
                ) for lnk in item.get("links", [])
            ]

            span = Span(
                id=uuid.uuid4(),
                project_id=uuid.UUID(project_id),
                trace_id=trace_id,
                span_id=item.get("span_id"),
                parent_span_id=item.get("parent_span_id"),
                name=item.get("name"),
                kind=item.get("kind"),
                start_time=datetime.datetime.fromisoformat(item.get("start_time")),
                end_time=datetime.datetime.fromisoformat(item.get("end_time")),
                duration_ms=item.get("duration_ms"),
                status_code=item.get("status_code"),
                status_message=item.get("status_message"),
                span_attributes=item.get("span_attributes", {}),
                resource_attributes=item.get("resource_attributes", {}),
                events=span_events,
                links=span_links
            )
            spans_to_insert.append(span)

    # 2. Persist to Postgres
    if events_to_insert or spans_to_insert:
        async with AsyncSessionLocal() as db:
            if events_to_insert:
                db.add_all(events_to_insert)
            
            if spans_to_insert:
                # Basic implementation: Assume new traces. 
                # Production would need upserts (ON CONFLICT DO NOTHING) for traces
                db.add_all(traces_to_insert.values())
                db.add_all(spans_to_insert)
                
            await db.commit()

        # 3. Publish to Redis PubSub for Real-time streaming
        pubsub_message = {
            "workspace_id": workspace_id,
            "project_id": project_id,
            "payload_type": payload_type,
            "data": data
        }
        redis_conn.publish(f"telemetry_stream:{workspace_id}", json.dumps(pubsub_message))
        
        # 4. Trigger Incident Detection
        # We do this async via an event or trigger, avoiding blocking the queue.
        # But for now we can just invoke it.
        asyncio.create_task(DetectionEngine.evaluate_telemetry(project_id, workspace_id, payload_type, data))

def process_telemetry_batch(payload_type: str, project_id: str, workspace_id: str, data: List[Dict[str, Any]]):
    """Entry point for RQ worker"""
    # RQ workers run synchronously, so we must run the async pipeline
    asyncio.run(_process_telemetry_batch_async(payload_type, project_id, workspace_id, data))
