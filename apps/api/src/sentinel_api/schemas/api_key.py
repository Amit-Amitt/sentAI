"""Pydantic schemas for API Key request validation and response serialization."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


API_KEY_ENVIRONMENTS = {"development", "production", "testing"}
API_KEY_SCOPES = {
    "incidents:read",
    "incidents:write",
    "reports:read",
    "reports:write",
    "logs:upload",
    "metrics:upload",
    "deployments:upload",
    "api-keys:manage",
    "workspace:read",
    "workspace:write",
}

API_KEY_SCOPE_ALIASES: dict[str, str] = {
    "incident:read": "incidents:read",
    "incident:write": "incidents:write",
    "report:read": "reports:read",
    "report:write": "reports:write",
    "apikey:manage": "api-keys:manage",
}


def normalize_api_key_scope(scope: str) -> str:
    """Map legacy scope names to canonical names."""

    normalized = scope.strip().lower()
    return API_KEY_SCOPE_ALIASES.get(normalized, normalized)


class ApiKeyCreate(BaseModel):
    """Payload for creating a secure API key."""

    name: str = Field(..., min_length=2, max_length=255, description="Unique label for the API Key")
    environment: str = Field(..., description="Target environment: production, development, testing")
    scopes: List[str] = Field(..., description="Assigned authorization permission scopes")
    expires_at: Optional[datetime] = Field(None, description="Optional key expiration date")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description of key usage")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in API_KEY_ENVIRONMENTS:
            raise ValueError("Environment must be one of: development, production, testing")
        return normalized

    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, value: List[str]) -> List[str]:
        normalized = [normalize_api_key_scope(scope) for scope in value]
        invalid = [scope for scope in normalized if scope not in API_KEY_SCOPES]
        if invalid:
            raise ValueError(f"Invalid API key scopes: {', '.join(sorted(set(invalid)))}")
        return normalized


class ApiKeyUpdate(BaseModel):
    """Payload for updating API key attributes."""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    scopes: Optional[List[str]] = Field(None)
    status: Optional[str] = Field(None)  # active, disabled, etc. (revocation is handled by specific endpoint)
    expires_at: Optional[datetime] = Field(None)

    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        normalized = [normalize_api_key_scope(scope) for scope in value]
        invalid = [scope for scope in normalized if scope not in API_KEY_SCOPES]
        if invalid:
            raise ValueError(f"Invalid API key scopes: {', '.join(sorted(set(invalid)))}")
        return normalized

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in {"active", "expired", "revoked", "disabled"}:
            raise ValueError("Invalid API key status")
        return normalized


class ApiKeyResponse(BaseModel):
    """Serialized API Key metadata (secret hash hidden)."""

    id: str
    name: str
    description: Optional[str] = None
    prefix: str
    environment: str
    scopes: List[str]
    created_by_id: Optional[str] = None
    created_at: str
    last_used_at: Optional[str] = None
    expires_at: Optional[str] = None
    status: str
    workspace_id: str


class ApiKeyWithSecretResponse(ApiKeyResponse):
    """Response containing the raw secret string (revealed ONLY once)."""

    secret: str


class ApiKeyListResponse(BaseModel):
    """List of workspace API keys."""

    results: List[ApiKeyResponse]
    total: int


class ApiKeyUsageResponse(BaseModel):
    """Serialized single request execution details."""

    id: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: str


class ApiKeyAuditResponse(BaseModel):
    """Serialized audit log tracking operations on keys."""

    id: str
    action: str
    performed_by_id: Optional[str] = None
    performed_by_name: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str


class ApiKeyAuditListResponse(BaseModel):
    """List of audit history rows for a key."""

    results: List[ApiKeyAuditResponse]
    total: int


class ApiKeyUsageStatsResponse(BaseModel):
    """Aggregated usage statistics and history for a key."""

    requests_today: int
    requests_this_month: int
    failed_requests: int
    successful_requests: int
    last_used_at: Optional[str] = None
    top_endpoint: Optional[str] = None
    recent_usages: List[ApiKeyUsageResponse]
    audit_history: List[ApiKeyAuditResponse]
