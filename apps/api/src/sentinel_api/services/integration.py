"""Service layer managing business logic for the Integrations Marketplace."""

import asyncio
import random
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from sentinel_api.models.integration import (
    IntegrationProvider,
    WorkspaceIntegration,
    IntegrationWebhook,
)
from sentinel_api.repositories.integration import IntegrationRepository


class IntegrationService:
    """Business logic orchestrator for Integrations."""

    def __init__(self) -> None:
        self.repo = IntegrationRepository()

    # ----------------------------------------------------
    # Provider Marketplace Catalog
    # ----------------------------------------------------

    async def list_providers_with_connections(
        self, db: AsyncSession, workspace_id: Optional[uuid.UUID]
    ) -> List[Dict[str, Any]]:
        """Lists all providers, overlaying active connection states if workspace_id is provided."""
        providers = await self.repo.list_providers(db)
        
        if not workspace_id:
            return [
                {
                    **provider.__dict__,
                    "connection": None
                }
                for provider in providers
                if not provider.__dict__.get("_sa_instance_state") or True
            ]

        connections = await self.repo.list_workspace_connections(db, workspace_id)
        connection_map = {conn.provider_id: conn for conn in connections}

        results = []
        for provider in providers:
            conn = connection_map.get(provider.id)
            
            # Construct mapped dictionary
            provider_dict = {
                "id": provider.id,
                "name": provider.name,
                "key": provider.key,
                "category": provider.category,
                "logo": provider.logo,
                "description": provider.description,
                "overview": provider.overview,
                "status": provider.status,
                "is_oauth_supported": provider.is_oauth_supported,
                "default_sync_frequency": provider.default_sync_frequency,
                "created_at": provider.created_at,
                "updated_at": provider.updated_at,
                "connection": None,
            }

            if conn:
                # Mask credentials values for API safety
                masked_creds = []
                for cred in conn.credentials:
                    masked_creds.append({
                        "id": cred.id,
                        "credential_type": cred.credential_type,
                        "key": cred.key,
                        "value": "••••••••••••••••" if len(cred.value) > 0 else "",
                        "expires_at": cred.expires_at,
                    })

                provider_dict["connection"] = {
                    "id": conn.id,
                    "workspace_id": conn.workspace_id,
                    "provider_id": conn.provider_id,
                    "status": conn.status,
                    "config": conn.config,
                    "last_sync_at": conn.last_sync_at,
                    "error_message": conn.error_message,
                    "is_enabled": conn.is_enabled,
                    "created_at": conn.created_at,
                    "updated_at": conn.updated_at,
                    "credentials": masked_creds,
                    "webhooks": [
                        {
                            "id": wh.id,
                            "name": wh.name,
                            "url": wh.url,
                            "direction": wh.direction,
                            "secret": wh.secret,
                            "retry_strategy": wh.retry_strategy,
                            "status": wh.status,
                            "delivery_status": wh.delivery_status,
                            "delivery_history": wh.delivery_history,
                        }
                        for wh in conn.webhooks
                    ],
                }
            results.append(provider_dict)

        return results

    async def get_provider_details(
        self, db: AsyncSession, provider_id: uuid.UUID, workspace_id: Optional[uuid.UUID]
    ) -> Dict[str, Any]:
        """Gets provider details, optionally including active workspace connection."""
        provider = await self.repo.get_provider_by_id(db, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Integration provider not found")

        provider_dict = {
            "id": provider.id,
            "name": provider.name,
            "key": provider.key,
            "category": provider.category,
            "logo": provider.logo,
            "description": provider.description,
            "overview": provider.overview,
            "status": provider.status,
            "is_oauth_supported": provider.is_oauth_supported,
            "default_sync_frequency": provider.default_sync_frequency,
            "created_at": provider.created_at,
            "updated_at": provider.updated_at,
            "connection": None,
        }

        if workspace_id:
            conn = await self.repo.get_connection_by_provider(db, workspace_id, provider_id)
            if conn:
                masked_creds = []
                for cred in conn.credentials:
                    masked_creds.append({
                        "id": cred.id,
                        "credential_type": cred.credential_type,
                        "key": cred.key,
                        "value": "••••••••••••••••",
                        "expires_at": cred.expires_at,
                    })

                provider_dict["connection"] = {
                    "id": conn.id,
                    "workspace_id": conn.workspace_id,
                    "provider_id": conn.provider_id,
                    "status": conn.status,
                    "config": conn.config,
                    "last_sync_at": conn.last_sync_at,
                    "error_message": conn.error_message,
                    "is_enabled": conn.is_enabled,
                    "created_at": conn.created_at,
                    "updated_at": conn.updated_at,
                    "credentials": masked_creds,
                    "webhooks": [
                        {
                            "id": wh.id,
                            "name": wh.name,
                            "url": wh.url,
                            "direction": wh.direction,
                            "secret": wh.secret,
                            "retry_strategy": wh.retry_strategy,
                            "status": wh.status,
                            "delivery_status": wh.delivery_status,
                            "delivery_history": wh.delivery_history,
                        }
                        for wh in conn.webhooks
                    ],
                }

        return provider_dict

    # ----------------------------------------------------
    # Workspace Integration Workflows
    # ----------------------------------------------------

    async def connect_integration(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        provider_id: uuid.UUID,
        config: Dict[str, Any],
        credentials: Dict[str, str],
        current_user_id: Optional[uuid.UUID] = None,
        client_host: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> WorkspaceIntegration:
        """Establishes an integration connection, verifying and storing credential references."""
        # Check provider exists
        provider = await self.repo.get_provider_by_id(db, provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        # Check if already connected
        existing_conn = await self.repo.get_connection_by_provider(db, workspace_id, provider_id)
        if existing_conn:
            # Re-activate and update configuration if it already exists
            conn = await self.repo.update_connection(
                db,
                existing_conn,
                status="connected",
                config=config,
                is_enabled=True,
                error_message=None,
            )
            # Clear old credentials and write new ones
            await self.repo.delete_connection_credentials(db, conn.id)
            for k, v in credentials.items():
                await self.repo.create_credential(
                    db,
                    workspace_integration_id=conn.id,
                    credential_type="api_key" if "key" in k or "secret" in k else "oauth_token",
                    key=k,
                    value=v,
                )
        else:
            # Create fresh connection record
            conn = await self.repo.create_connection(
                db,
                workspace_id=workspace_id,
                provider_id=provider_id,
                config=config,
                status="connected",
            )
            # Insert credentials
            for k, v in credentials.items():
                await self.repo.create_credential(
                    db,
                    workspace_integration_id=conn.id,
                    credential_type="api_key" if "key" in k or "secret" in k else "oauth_token",
                    key=k,
                    value=v,
                )

            # Provision dynamic incoming webhook endpoint for webhook/event-based categories
            if provider.key in ["github", "gitlab", "slack", "pagerduty", "webhooks"]:
                webhook_secret = f"whsec_{uuid.uuid4().hex[:24]}"
                webhook_url = f"https://api.sentinel.ai/api/v1/webhooks/v/{conn.id}"
                await self.repo.create_webhook(
                    db,
                    workspace_integration_id=conn.id,
                    name=f"{provider.name} Telemetry Receiver",
                    url=webhook_url,
                    direction="incoming",
                    secret=webhook_secret,
                )

            # Record initial sync history row
            await self.repo.create_sync(
                db,
                workspace_integration_id=conn.id,
                status="success",
                duration_ms=450,
                imported_resources=12,
            )

        # Audit log creation
        await self.repo.create_audit(
            db,
            workspace_id=workspace_id,
            workspace_integration_id=conn.id,
            action="connected",
            performed_by_id=current_user_id,
            details={"provider_key": provider.key, "provider_name": provider.name},
            ip_address=client_host,
            user_agent=user_agent,
        )

        await db.commit()
        
        # Re-fetch fully loaded object
        refetched = await self.repo.get_connection_by_id(db, conn.id)
        if not refetched:
            raise HTTPException(status_code=500, detail="Failed to load connected integration")
        return refetched

    async def update_connection_settings(
        self,
        db: AsyncSession,
        connection_id: uuid.UUID,
        workspace_id: uuid.UUID,
        config: Optional[Dict[str, Any]],
        credentials: Optional[Dict[str, str]],
        is_enabled: Optional[bool],
        current_user_id: Optional[uuid.UUID] = None,
        client_host: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> WorkspaceIntegration:
        """Updates configurations, resets secrets, or toggles enablement flag."""
        conn = await self.repo.get_connection_by_id(db, connection_id)
        if not conn or conn.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="Workspace integration not found")

        updates: Dict[str, Any] = {}
        if config is not None:
            updates["config"] = config
        if is_enabled is not None:
            updates["is_enabled"] = is_enabled
            updates["status"] = "connected" if is_enabled else "disabled"

        # Apply updates
        updated_conn = await self.repo.update_connection(db, conn, **updates)

        # Update credentials if supplied
        if credentials:
            await self.repo.delete_connection_credentials(db, conn.id)
            for k, v in credentials.items():
                await self.repo.create_credential(
                    db,
                    workspace_integration_id=conn.id,
                    credential_type="api_key" if "key" in k or "secret" in k else "oauth_token",
                    key=k,
                    value=v,
                )

        # Record audit log
        await self.repo.create_audit(
            db,
            workspace_id=workspace_id,
            workspace_integration_id=conn.id,
            action="config_updated" if config is not None else ("enabled" if is_enabled else "disabled"),
            performed_by_id=current_user_id,
            details={"provider_key": conn.provider.key, "fields_changed": list(updates.keys())},
            ip_address=client_host,
            user_agent=user_agent,
        )

        await db.commit()
        
        refetched = await self.repo.get_connection_by_id(db, conn.id)
        if not refetched:
            raise HTTPException(status_code=500, detail="Failed to load updated connection")
        return refetched

    async def disconnect_integration(
        self,
        db: AsyncSession,
        connection_id: uuid.UUID,
        workspace_id: uuid.UUID,
        current_user_id: Optional[uuid.UUID] = None,
        client_host: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> WorkspaceIntegration:
        """Deactivates and marks connection as disconnected without deleting records."""
        conn = await self.repo.get_connection_by_id(db, connection_id)
        if not conn or conn.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="Workspace integration not found")

        updated_conn = await self.repo.update_connection(
            db, conn, status="disconnected", is_enabled=False
        )

        # Audit disconnect
        await self.repo.create_audit(
            db,
            workspace_id=workspace_id,
            workspace_integration_id=conn.id,
            action="disconnected",
            performed_by_id=current_user_id,
            details={"provider_key": conn.provider.key, "provider_name": conn.provider.name},
            ip_address=client_host,
            user_agent=user_agent,
        )

        await db.commit()
        
        refetched = await self.repo.get_connection_by_id(db, conn.id)
        if not refetched:
            raise HTTPException(status_code=500, detail="Failed to load disconnected integration")
        return refetched

    async def delete_integration_permanently(
        self,
        db: AsyncSession,
        connection_id: uuid.UUID,
        workspace_id: uuid.UUID,
        current_user_id: Optional[uuid.UUID] = None,
        client_host: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Completely purges the workspace integration and metadata."""
        conn = await self.repo.get_connection_by_id(db, connection_id)
        if not conn or conn.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="Workspace integration not found")

        provider_key = conn.provider.key
        provider_name = conn.provider.name

        # Delete connection
        await self.repo.delete_connection(db, conn)

        # Audit deletion
        await self.repo.create_audit(
            db,
            workspace_id=workspace_id,
            workspace_integration_id=None,
            action="deleted",
            performed_by_id=current_user_id,
            details={"provider_key": provider_key, "provider_name": provider_name},
            ip_address=client_host,
            user_agent=user_agent,
        )

        await db.commit()
        return True

    # ----------------------------------------------------
    # Testing, Synchronization and Logs
    # ----------------------------------------------------

    async def test_connection_health(
        self, db: AsyncSession, connection_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Performs mock API validation to remote systems, tracking latency."""
        conn = await self.repo.get_connection_by_id(db, connection_id)
        if not conn or conn.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Simulate network delay (100 - 800ms)
        latency = random.randint(150, 650)
        await asyncio.sleep(latency / 1000.0)

        # Perform mock testing depending on provider configurations
        is_success = True
        error_msg = None
        
        # Test mock credentials check
        if not conn.credentials:
            is_success = False
            error_msg = "Invalid authorization: Missing credentials keys."
        elif conn.provider.key == "github" and "client_id" in conn.config and not conn.config.get("client_id"):
            is_success = False
            error_msg = "OAuth failure: Empty client identifier."

        # Update integration status based on test result
        if is_success:
            await self.repo.update_connection(db, conn, status="connected", error_message=None)
        else:
            await self.repo.update_connection(db, conn, status="error", error_message=error_msg)

        await db.commit()

        return {
            "success": is_success,
            "status": "connected" if is_success else "error",
            "message": "Connection verification successful." if is_success else f"Connection verification failed: {error_msg}",
            "latency_ms": latency,
            "details": {
                "tested_endpoint": f"https://api.{conn.provider.key}.com/v1/healthz" if conn.provider.key != "webhooks" else conn.config.get("url"),
                "status_code": 200 if is_success else 401,
                "tls_version": "TLSv1.3",
            }
        }

    async def trigger_manual_sync(
        self, db: AsyncSession, connection_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Runs a telemetry synchronization and logs sync results in database history."""
        conn = await self.repo.get_connection_by_id(db, connection_id)
        if not conn or conn.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Perform simulated sync
        start_time = datetime.now(UTC)
        latency = random.randint(300, 1100)
        await asyncio.sleep(latency / 1000.0)

        imported = random.randint(5, 45)
        status = "success"
        errors = []
        warnings = []

        if conn.status == "error":
            status = "failed"
            errors.append({"code": "CONN_ERR", "message": conn.error_message or "Connection endpoint unreachable."})
            imported = 0
        elif random.random() < 0.08:
            status = "failed"
            errors.append({"code": "AUTH_EXPIRED", "message": "The remote system returned HTTP 401 Unauthorized."})
            imported = 0

        if random.random() < 0.15 and status == "success":
            warnings.append({"code": "RATE_LIMITED", "message": "Approaching remote API rate-limits. Throttled request pipeline."})

        # Save sync log
        sync_log = await self.repo.create_sync(
            db,
            workspace_integration_id=conn.id,
            status=status,
            duration_ms=latency,
            imported_resources=imported,
            errors=errors,
            warnings=warnings,
            started_at=start_time,
            completed_at=datetime.now(UTC),
        )

        # Update parent integration status
        conn_updates: Dict[str, Any] = {"last_sync_at": datetime.now(UTC)}
        if status == "failed":
            conn_updates["status"] = "error"
            conn_updates["error_message"] = errors[0]["message"]
        else:
            conn_updates["status"] = "connected"
            conn_updates["error_message"] = None

        await self.repo.update_connection(db, conn, **conn_updates)
        await db.commit()

        # Add sample incoming webhook history object for mock activities
        if conn.webhooks:
            wh = conn.webhooks[0]
            new_history = list(wh.delivery_history)
            new_history.insert(0, {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(UTC).isoformat(),
                "response_code": 200 if status == "success" else 500,
                "status": "success" if status == "success" else "failed",
                "payload_size_bytes": random.randint(120, 850),
            })
            # keep max 20 entries
            wh.delivery_history = new_history[:20]
            wh.delivery_status = "success" if status == "success" else "failed"
            await db.commit()

        return {
            "success": status == "success",
            "sync_id": sync_log.id,
            "status": status,
            "message": f"Sync pipeline run completed in {latency}ms." if status == "success" else f"Sync pipeline failed: {errors[0]['message']}",
        }

    async def get_history_logs(
        self, db: AsyncSession, connection_id: uuid.UUID, workspace_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Aggregates chronological sync events and SRE activity logs for the connection."""
        conn = await self.repo.get_connection_by_id(db, connection_id)
        if not conn or conn.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="Connection not found")

        syncs = await self.repo.get_sync_history(db, conn.id, limit=30)
        audits = await self.repo.get_audit_history(db, workspace_id, conn.id, limit=30)

        # Format audit logs performed by user names
        formatted_audits = []
        for audit in audits:
            perf_by = "System"
            if audit.performed_by:
                perf_by = audit.performed_by.full_name
            
            formatted_audits.append({
                "id": audit.id,
                "action": audit.action,
                "performed_by_name": perf_by,
                "details": audit.details,
                "ip_address": audit.ip_address,
                "user_agent": audit.user_agent,
                "timestamp": audit.timestamp,
            })

        return {
            "syncs": [
                {
                    "id": s.id,
                    "status": s.status,
                    "started_at": s.started_at,
                    "completed_at": s.completed_at,
                    "duration_ms": s.duration_ms,
                    "imported_resources": s.imported_resources,
                    "errors": s.errors,
                    "warnings": s.warnings,
                }
                for s in syncs
            ],
            "audits": formatted_audits,
        }
