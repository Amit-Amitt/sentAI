import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from sentinel_api.exceptions import AppException
from sentinel_api.schemas.error import ErrorDetail, ErrorResponse

logger = structlog.get_logger("sentinel_api.exception")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handles custom application exceptions."""
    logger.error(
        "Application exception occurred",
        path=request.url.path,
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
    )

    response_content = ErrorResponse(
        success=False,
        error_code=exc.error_code,
        message=exc.message,
    ).model_dump()

    return JSONResponse(status_code=exc.status_code, content=response_content)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handles Pydantic input validation errors."""
    logger.error(
        "Validation error occurred",
        path=request.url.path,
        details=exc.errors(),
    )

    details = [
        ErrorDetail(loc=list(err["loc"]), msg=err["msg"], type=err["type"])
        for err in exc.errors()
    ]

    response_content = ErrorResponse(
        success=False,
        error_code="VALIDATION_ERROR",
        message="Request payload validation failed",
        details=details,
    ).model_dump()

    return JSONResponse(status_code=422, content=response_content)


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handles Starlette/FastAPI standard HTTP exceptions."""
    logger.error(
        "HTTP exception occurred",
        path=request.url.path,
        status_code=exc.status_code,
        message=exc.detail,
    )

    response_content = ErrorResponse(
        success=False,
        error_code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
    ).model_dump()

    return JSONResponse(status_code=exc.status_code, content=response_content)


async def unexpected_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handles unexpected raw python exceptions."""
    logger.exception(
        "Unexpected server error occurred",
        path=request.url.path,
        error=str(exc),
    )

    response_content = ErrorResponse(
        success=False,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred. Please try again later.",
    ).model_dump()

    return JSONResponse(status_code=500, content=response_content)


from sentinel_api.ai.exceptions import AIPlatformException


async def ai_platform_exception_handler(
    request: Request, exc: AIPlatformException
) -> JSONResponse:
    """Handles custom AI platform exceptions."""
    logger.error(
        "AI platform exception occurred",
        path=request.url.path,
        error=str(exc),
    )

    response_content = ErrorResponse(
        success=False,
        error_code="AI_PLATFORM_ERROR",
        message=str(exc),
    ).model_dump()

    return JSONResponse(status_code=400, content=response_content)


def register_exception_handlers(app: FastAPI) -> None:
    """Registers all exception handlers on the FastAPI application instance."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(AIPlatformException, ai_platform_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unexpected_exception_handler)

