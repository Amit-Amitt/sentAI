import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import String, JSON, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_api.database.base import BaseModel


class UserSession(BaseModel):
    """Tracks active sessions, refresh tokens, and device information."""
    __tablename__ = "user_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    refresh_token_jti: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SystemRole(BaseModel):
    """RBAC Role definitions (e.g., Owner, Admin, Developer, SRE)."""
    __tablename__ = "system_roles"

    # Allow custom roles per organization, or leave null for global default roles
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=True)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # E.g. ["incidents:read", "incidents:write", "settings:admin"]
    permissions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)


class ServiceAccount(BaseModel):
    """Identity for machine-to-machine interactions or CI/CD pipelines."""
    __tablename__ = "service_accounts"

    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ApiToken(BaseModel):
    """Secure API Tokens linked to Users or Service Accounts."""
    __tablename__ = "api_tokens"

    # Polymorphic ownership (User OR Service Account)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    service_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("service_accounts.id", ondelete="CASCADE"), index=True, nullable=True)
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Store hashed/encrypted token logic. The raw token is only shown once.
    token_hash: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    prefix: Mapped[str] = mapped_column(String, nullable=False) # e.g. sent_xxxx...
    
    scopes: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AuditLog(BaseModel):
    """Immutable ledger of all security-relevant events across the platform."""
    __tablename__ = "audit_logs"

    # Tracking Context
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    service_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("service_accounts.id", ondelete="SET NULL"), index=True, nullable=True)
    
    action: Mapped[str] = mapped_column(String, index=True, nullable=False) # E.g. user.login, api_key.create, role.update
    status: Mapped[str] = mapped_column(String, nullable=False) # success, failure
    
    # Request Details
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Detailed payload
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
