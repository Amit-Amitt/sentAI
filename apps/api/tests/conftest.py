from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Override settings for testing environment
from sentinel_api.config.settings import settings

settings.APP_ENV = "testing"
settings.DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Compile PostgreSQL JSONB to SQLite JSON during test runs
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(element, compiler, **kw):
    return "JSON"

from sentinel_api.app import app as fastapi_app  # noqa: E402
from sentinel_api.database.session import get_db_session  # noqa: E402


@pytest.fixture
async def mock_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a mocked SQLAlchemy AsyncSession for testing."""
    session = AsyncMock(spec=AsyncSession)
    yield session


@pytest.fixture(autouse=True)
def override_db_dependency(
    mock_db_session: AsyncSession,
) -> Generator[None, None, None]:
    """Automatically overrides get_db_session with mock_db_session for all tests."""

    async def _get_db_session_override():
        yield mock_db_session

    fastapi_app.dependency_overrides[get_db_session] = _get_db_session_override
    yield
    fastapi_app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture
def app() -> FastAPI:
    """Returns the FastAPI application instance."""
    return fastapi_app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Provides an HTTPX AsyncClient configured to test the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
