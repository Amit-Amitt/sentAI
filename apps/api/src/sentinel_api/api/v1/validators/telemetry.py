from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class TelemetryEventPayload(BaseModel):
    event_type: str = Field(..., description="LOG, METRIC, EXCEPTION, REQUEST, HEARTBEAT, EVENT, DEPLOYMENT, HEALTH")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    data: Dict[str, Any] = Field(..., description="Payload data")
    
class TelemetryBatchRequest(BaseModel):
    events: List[TelemetryEventPayload] = Field(..., description="Batch of telemetry events")

class LogPayload(BaseModel):
    level: str
    message: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str

class LogBatchRequest(BaseModel):
    logs: List[LogPayload]

class MetricPayload(BaseModel):
    name: str
    value: float
    tags: Optional[Dict[str, str]] = None
    timestamp: str

class MetricBatchRequest(BaseModel):
    metrics: List[MetricPayload]

class EventPayload(BaseModel):
    name: str
    payload: Dict[str, Any]
    timestamp: str

class EventBatchRequest(BaseModel):
    events: List[EventPayload]

class ExceptionPayload(BaseModel):
    type: Optional[str] = None
    message: str
    stack_trace: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    timestamp: str

class ExceptionBatchRequest(BaseModel):
    exceptions: List[ExceptionPayload]

class HeartbeatPayload(BaseModel):
    environment: str
    version: str
    cpu: float
    memory: float
    health: str
    timestamp: str

class HeartbeatBatchRequest(BaseModel):
    heartbeats: List[HeartbeatPayload]

class DeploymentPayload(BaseModel):
    version: str
    environment: str
    status: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: str

class DeploymentBatchRequest(BaseModel):
    deployments: List[DeploymentPayload]

class HealthPayload(BaseModel):
    service_name: str
    status: str
    latency_ms: Optional[float] = None
    timestamp: str

class HealthBatchRequest(BaseModel):
    health_checks: List[HealthPayload]
