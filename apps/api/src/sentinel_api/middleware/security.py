"""Middleware preparing API Key Authentication, Rate Limiting, Scope/Permission Validation, Workspace Isolation."""

import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import structlog

from sentinel_api.database.session import AsyncSessionLocal
from sentinel_api.services.api_key import ApiKeyService

# Simple in-memory rate limiting store (key -> list of request timestamps)
# In production, this should be replaced with Redis.
RATE_LIMIT_STORE: dict[str, list[float]] = {}
RATE_LIMIT_WINDOW = 60.0  # seconds
RATE_LIMIT_MAX_REQUESTS = 60  # per window


class ApiKeySecurityMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing API Key authentication, rate-limiting, and scopes validation."""

    def __init__(self, app, service: ApiKeyService | None = None) -> None:
        super().__init__(app)
        self.service = service or ApiKeyService()

    def _is_rate_limited(self, key_id: str) -> bool:
        """Enforces a mock rate limiting count per API Key."""
        now = time.time()
        timestamps = RATE_LIMIT_STORE.setdefault(key_id, [])

        # Filter out outdated timestamps
        timestamps[:] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]

        if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
            return True

        timestamps.append(now)
        return False

    def _get_required_scope(self, path: str, method: str) -> str | None:
        """Determines the required permission scope based on the HTTP request method and path."""
        method = method.upper()

        if "/incidents" in path:
            return "incidents:read" if method in {"GET", "HEAD"} else "incidents:write"
        if "/reports" in path:
            return "reports:read" if method in {"GET", "HEAD"} else "reports:write"
        if "/logs" in path or "/upload-logs" in path:
            return "logs:upload"
        if "/metrics" in path or "/upload-metrics" in path:
            return "metrics:upload"
        if "/deployments" in path:
            return "deployments:upload"
        if "/workspaces" in path:
            return "workspace:read" if method in {"GET", "HEAD"} else "workspace:write"
        if "/apikeys" in path:
            return "api-keys:manage"

        return None

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Check for X-API-Key header (support both X-API-Key and Authorization Bearer sent_...)
        raw_key = request.headers.get("X-API-Key")
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.lower().startswith("bearer "):
            bearer_token = auth_header[7:]
            if bearer_token.startswith("sent_"):
                raw_key = bearer_token

        # If no API Key header is present, bypass key checks (allow JWT/session users)
        if not raw_key:
            return await call_next(request)

        # Open DB session specifically for the middleware operations
        async with AsyncSessionLocal() as db:
            try:
                # 1. API Key Authentication
                api_key = await self.service.validate_key(db, raw_key)
                if not api_key:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "success": False,
                            "error": "Unauthorized: Invalid, expired, or revoked API Key.",
                            "code": "UNAUTHORIZED_KEY",
                        },
                    )

                key_id_str = str(api_key.id)

                # Initialize tracking variables
                status_code = 200
                process_time_ms = 0
                start_time = time.perf_counter()
                response = None

                # 2. Rate Limiting
                if self._is_rate_limited(key_id_str):
                    status_code = 429
                    response = JSONResponse(
                        status_code=429,
                        content={
                            "success": False,
                            "error": "Too Many Requests: API rate limit exceeded.",
                            "code": "RATE_LIMIT_EXCEEDED",
                        },
                    )

                # 3. Workspace Isolation
                if not response:
                    req_ws_id = request.headers.get("X-Workspace-ID") or request.query_params.get("workspace_id")
                    if req_ws_id:
                        try:
                            if str(api_key.workspace_id) != str(req_ws_id):
                                status_code = 403
                                response = JSONResponse(
                                    status_code=403,
                                    content={
                                        "success": False,
                                        "error": "Forbidden: Workspace mismatch isolation.",
                                        "code": "WORKSPACE_ISOLATION_VIOLATION",
                                    },
                                )
                        except ValueError:
                            status_code = 400
                            response = JSONResponse(
                                status_code=400,
                                content={
                                    "success": False,
                                    "error": "Bad Request: Invalid Workspace ID format.",
                                    "code": "INVALID_WORKSPACE_ID",
                                },
                            )

                # 4. Scope / Permission Validation
                if not response:
                    required_scope = self._get_required_scope(request.url.path, request.method)
                    if required_scope:
                        key_scopes = {p.scope for p in api_key.permissions}
                        if required_scope not in key_scopes:
                            status_code = 403
                            response = JSONResponse(
                                status_code=403,
                                content={
                                    "success": False,
                                    "error": f"Forbidden: Key is missing scope '{required_scope}' required for this resource.",
                                    "code": "INSUFFICIENT_SCOPE",
                                },
                            )

                # 5. Execute request if all checks pass
                if not response:
                    response = await call_next(request)
                    status_code = response.status_code

                process_time_ms = int((time.perf_counter() - start_time) * 1000)

                # 6. Usage Tracking (Log usage metrics in DB)
                try:
                    ip_address = request.client.host if request.client else None
                    user_agent = request.headers.get("user-agent")

                    await self.service.track_usage(
                        db=db,
                        api_key_id=api_key.id,
                        endpoint=request.url.path,
                        method=request.method,
                        status_code=status_code,
                        response_time_ms=process_time_ms,
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                    await db.commit()  # Save usage tracking
                except Exception as usage_err:
                    structlog.get_logger("sentinel_api.middleware.security").error(
                        "Failed to track API Key usage", error=str(usage_err)
                    )

                return response

            except Exception as err:
                await db.rollback()
                structlog.get_logger("sentinel_api.middleware.security").exception(
                    "Error executing security middleware check", error=str(err)
                )
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": "Internal server error during authentication verification.",
                        "code": "INTERNAL_AUTH_ERROR",
                    },
                )
