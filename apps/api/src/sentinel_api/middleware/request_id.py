import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to assign a unique request ID (Correlation ID) to every request.

    Binds the ID to structlog's contextvars for log correlation, and returns
    it in the response headers.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Check for existing request ID header, otherwise generate one
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Bind to structlog context variables
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # Allow downstream processors to access the request ID via state
        request.state.request_id = request_id

        # Process the request
        response = await call_next(request)

        # Set the header on the response
        response.headers["X-Request-ID"] = request_id
        return response
