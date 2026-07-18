"""Pydantic schemas for the Integrations Marketplace."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ----------------------------------------------------
# Integration Provider Schemas
# ----------------------------------------------------

class IntegrationProviderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    key: str
    category: str
    logo: str
    description: str
    overview: str
    status: str
    is_oauth_supported: bool
    default_sync_frequency: str
    created_at: datetime
    updated_at: datetime
    
    # Nested workspace connection details if queried in workspace scope
    connection: Optional[Any] = None


class IntegrationProviderListResponse(BaseModel):
    results: List[IntegrationProviderResponse]
    total: int


# ----------------------------------------------------
# Workspace Integration Schemas
# ----------------------------------------------------

class IntegrationCredentialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    credential_type: str
    key: str
    value: str = Field(description="Masked or secure reference value")
    expires_at: Optional[datetime] = None


class IntegrationWebhookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    url: str
    direction: str
    secret: Optional[str] = None
    retry_strategy: Dict[str, Any]
    status: str
    delivery_status: Optional[str] = None
    delivery_history: List[Dict[str, Any]] = []


class IntegrationSyncResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: int
    imported_resources: int
    errors: List[Any]
    warnings: List[Any]


class IntegrationAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    action: str
    performed_by_name: Optional[str] = None
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime


class WorkspaceIntegrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    provider_id: uuid.UUID
    provider: IntegrationProviderResponse
    status: str
    config: Dict[str, Any]
    last_sync_at: Optional[datetime] = None
    error_message: Optional[str] = None
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    credentials: List[IntegrationCredentialResponse] = []
    webhooks: List[IntegrationWebhookResponse] = []


class WorkspaceIntegrationListResponse(BaseModel):
    results: List[WorkspaceIntegrationResponse]
    total: int


# ----------------------------------------------------
# Request Payload Schemas
# ----------------------------------------------------

class WorkspaceIntegrationCreate(BaseModel):
    provider_id: uuid.UUID
    name: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    credentials: Dict[str, str] = Field(
        default_factory=dict, 
        description="Keys and secret values (e.g. {'api_key': 'xyz', 'client_secret': 'abc'})"
    )


class WorkspaceIntegrationUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, str]] = None
    is_enabled: Optional[bool] = None


class ConnectionTestResponse(BaseModel):
    success: bool
    status: str
    message: str
    latency_ms: int
    details: Dict[str, Any] = Field(default_factory=dict)


class SyncTriggerResponse(BaseModel):
    success: bool
    sync_id: uuid.UUID
    status: str
    message: str


class IntegrationHistoryResponse(BaseModel):
    syncs: List[IntegrationSyncResponse]
    audits: List[IntegrationAuditResponse]
