import uvicorn

from sentinel_api.config.settings import settings

if __name__ == "__main__":
    # Disable default uvicorn log configuration to let
    # structlog manage all output formatters
    uvicorn.run(
        "sentinel_api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.is_dev,
        log_config=None,
    )
