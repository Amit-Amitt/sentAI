"""Service layer for API Key business logic."""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Tuple

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.exceptions import EntityNotFoundException, ValidationException
from sentinel_api.models.api_key import ApiKey
from sentinel_api.repositories.api_key import ApiKeyRepository
from sentinel_api.schemas.api_key import normalize_api_key_scope

logger = structlog.get_logger("sentinel_api.services.api_key")


class ApiKeyService:
    """Orchestrates API key lifecycles, security validations, and analytics logging."""

    VALID_SCOPES = {
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

    VALID_ENVIRONMENTS = {"production", "development", "testing"}

    def __init__(self) -> None:
        self.repo = ApiKeyRepository()

    def _generate_secret(self, environment: str) -> Tuple[str, str, str]:
        """Generates a secure API key string and its metadata.

        Returns:
            Tuple of (raw_key, prefix_preview, secret_hash)
        """
        is_live = environment.lower() == "production"
        prefix = "sent_live_" if is_live else "sent_test_"

        # Generate 32 characters of high-entropy key secret
        secret_part = secrets.token_urlsafe(32)
        raw_key = f"{prefix}{secret_part}"

        # Prefix preview shows environment and first 6 chars of secret (e.g. sent_live_ab12cd...)
        prefix_preview = f"{prefix}{secret_part[:6]}..."

        # Hash secret using SHA-256
        secret_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

        return raw_key, prefix_preview, secret_hash

    def _normalize_scopes(self, scopes: List[str]) -> List[str]:
        normalized = [normalize_api_key_scope(scope) for scope in scopes]
        invalid_scopes = [scope for scope in normalized if scope not in self.VALID_SCOPES]
        if invalid_scopes:
            raise ValidationException(
                f"Invalid scopes: {', '.join(sorted(set(invalid_scopes)))}. Must be from allowed scopes.",
                error_code="INVALID_SCOPES",
            )
        return normalized

    async def create_key(
        self,
        db: AsyncSession,
        workspace_id: uuid.UUID,
        name: str,
        environment: str,
        scopes: List[str],
        created_by_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[ApiKey, str]:
        """Creates a secure API Key, hashes it, and returns it along with the raw key."""
        # Validate environment
        environment = environment.strip().lower()
        if environment not in self.VALID_ENVIRONMENTS:
            raise ValidationException(
                f"Invalid environment: {environment}. Must be production, development, or testing.",
                error_code="INVALID_ENVIRONMENT",
            )

        # Validate scopes
        scopes = self._normalize_scopes(scopes)

        raw_key, prefix, secret_hash = self._generate_secret(environment)

        api_key = await self.repo.create(
            db=db,
            name=name,
            prefix=prefix,
            secret_hash=secret_hash,
            environment=environment,
            workspace_id=workspace_id,
            created_by_id=created_by_id,
            description=description,
            expires_at=expires_at,
            scopes=scopes,
        )

        # Write audit log
        await self.repo.create_audit(
            db=db,
            api_key_id=api_key.id,
            action="created",
            performed_by_id=created_by_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "name": name,
                "environment": environment,
                "scopes": scopes,
                "expires_at": expires_at.isoformat() if expires_at else None,
            },
        )

        logger.info(
            "API Key created",
            api_key_id=str(api_key.id),
            prefix=prefix,
            workspace_id=str(workspace_id),
        )

        return api_key, raw_key

    async def get_key(self, db: AsyncSession, api_key_id: uuid.UUID) -> ApiKey:
        """Retrieves an API Key by ID or raises 404."""
        api_key = await self.repo.get_by_id(db, api_key_id)
        if not api_key:
            raise EntityNotFoundException(
                f"API Key not found: {api_key_id}",
                error_code="API_KEY_NOT_FOUND",
            )
        return api_key

    async def list_keys(
        self, db: AsyncSession, workspace_id: uuid.UUID
    ) -> List[ApiKey]:
        """Lists all keys configured for a workspace."""
        return await self.repo.list_by_workspace(db, workspace_id)

    async def update_key(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        performed_by_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        **kwargs: object,
    ) -> ApiKey:
        """Updates API Key fields and creates appropriate audit log logs."""
        api_key = await self.get_key(db, api_key_id)

        # Validate scopes if provided
        if scopes is not None:
            invalid_scopes = [s for s in scopes if s not in self.VALID_SCOPES]
            if invalid_scopes:
                raise ValidationException(
                    f"Invalid scopes: {', '.join(invalid_scopes)}",
                    error_code="INVALID_SCOPES",
                )

        audit_events: List[Tuple[str, Dict[str, Any]]] = []
        if "name" in kwargs and kwargs["name"] != api_key.name:
            audit_events.append(
                (
                    "renamed",
                    {
                        "old_name": api_key.name,
                        "new_name": kwargs["name"],
                    },
                )
            )

        if scopes is not None and set(scopes) != {p.scope for p in api_key.permissions}:
            audit_events.append(
                (
                    "scope_changed",
                    {
                        "old_scopes": [p.scope for p in api_key.permissions],
                        "new_scopes": scopes,
                    },
                )
            )

        if "expires_at" in kwargs:
            new_exp = kwargs["expires_at"]
            old_exp = api_key.expires_at
            if new_exp != old_exp:
                audit_events.append(
                    (
                        "expiration_changed",
                        {
                            "old_expires_at": old_exp.isoformat() if old_exp else None,
                            "new_expires_at": (
                                new_exp.isoformat() if isinstance(new_exp, datetime) else str(new_exp)
                            ),
                        },
                    )
                )

        updated_key = await self.repo.update(db, api_key, scopes=scopes, **kwargs)

        for action, audit_details in audit_events:
            await self.repo.create_audit(
                db=db,
                api_key_id=updated_key.id,
                action=action,
                performed_by_id=performed_by_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=audit_details,
            )

        logger.info("API Key updated", api_key_id=str(api_key_id))
        return updated_key

    async def rotate_key(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        performed_by_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[ApiKey, str]:
        """Rotates key secret.

        Generates a new secret, hashes it, marks key active, and logs audit record.
        """
        api_key = await self.get_key(db, api_key_id)

        raw_key, prefix, secret_hash = self._generate_secret(api_key.environment)

        old_prefix = api_key.prefix

        updated_key = await self.repo.update(
            db=db,
            api_key=api_key,
            prefix=prefix,
            secret_hash=secret_hash,
            status="active",
        )

        # Audit rotation
        await self.repo.create_audit(
            db=db,
            api_key_id=updated_key.id,
            action="rotated",
            performed_by_id=performed_by_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "old_prefix": old_prefix,
                "new_prefix": prefix,
            },
        )

        logger.info("API Key rotated", api_key_id=str(api_key_id), prefix=prefix)
        return updated_key, raw_key

    async def copy_key(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        performed_by_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ApiKey:
        """Records a key copy action for audit history."""
        api_key = await self.get_key(db, api_key_id)
        await self.repo.create_audit(
            db=db,
            api_key_id=api_key.id,
            action="copied",
            performed_by_id=performed_by_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"prefix": api_key.prefix, "environment": api_key.environment},
        )
        return api_key

    async def revoke_key(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        performed_by_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ApiKey:
        """Revokes an API Key, preventing any future access usage."""
        api_key = await self.get_key(db, api_key_id)
        if api_key.status == "revoked":
            return api_key

        updated_key = await self.repo.update(db=db, api_key=api_key, status="revoked")

        # Audit revocation
        await self.repo.create_audit(
            db=db,
            api_key_id=updated_key.id,
            action="revoked",
            performed_by_id=performed_by_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info("API Key revoked", api_key_id=str(api_key_id))
        return updated_key

    async def delete_key(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        performed_by_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Deletes an API Key record entirely."""
        api_key = await self.get_key(db, api_key_id)
        await self.repo.delete(db, api_key)
        logger.info("API Key deleted", api_key_id=str(api_key_id))
        return True

    async def get_usage_analytics(
        self, db: AsyncSession, api_key_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Gathers usage stats, metrics, and audit history logs."""
        # Check that key exists first
        await self.get_key(db, api_key_id)
        return await self.repo.get_usage_statistics(db, api_key_id)

    async def get_audit_history(
        self, db: AsyncSession, api_key_id: uuid.UUID
    ) -> List[Any]:
        """Returns audit events for a key."""
        await self.get_key(db, api_key_id)
        return await self.repo.get_audits(db, api_key_id)

    async def track_usage(
        self,
        db: AsyncSession,
        api_key_id: uuid.UUID,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Saves a request usage metric row."""
        await self.repo.create_usage(
            db=db,
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def validate_key(self, db: AsyncSession, raw_key: str) -> Optional[ApiKey]:
        """Validates a raw API Key string.

        Checks signature, status, and expiration. Automatically transitions
        status to 'expired' and audits it if expired.
        """
        # Hash raw key to lookup in DB
        secret_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        api_key = await self.repo.get_by_hash(db, secret_hash)

        if not api_key:
            return None

        if api_key.status != "active":
            return None

        # Check expiration date
        if api_key.expires_at and api_key.expires_at < datetime.now(UTC):
            # Transition to expired
            await self.repo.update(db=db, api_key=api_key, status="expired")
            # Log expired audit
            await self.repo.create_audit(
                db=db,
                api_key_id=api_key.id,
                action="expired",
                details={"expired_at": api_key.expires_at.isoformat()},
            )
            logger.info("API Key expired during validation check", api_key_id=str(api_key.id))
            return None

        return api_key
