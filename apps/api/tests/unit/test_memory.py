import uuid
from typing import AsyncGenerator
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sentinel_api.app import app as fastapi_app
from sentinel_api.database.base import Base
from sentinel_api.database.session import get_db_session
from sentinel_api.models.memory import IncidentMemory, IncidentTag
from sentinel_api.models.workspace import Workspace
from sentinel_api.models.organization import Organization


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture providing a clean in-memory SQLite database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    import sentinel_api.models  # noqa: F401
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_maker() as session:
        yield session
        await session.rollback()
        
    await engine.dispose()


@pytest.fixture
def app(db_session: AsyncSession) -> FastAPI:
    """Returns the FastAPI application instance with mocked DB dependency."""
    async def _get_db_session_override():
        yield db_session

    fastapi_app.dependency_overrides[get_db_session] = _get_db_session_override
    yield fastapi_app
    fastapi_app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Provides an HTTPX AsyncClient configured to test the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def admin_headers():
    return {"Authorization": "Bearer test-admin-token"}


from sentinel_api.models.user import User

@pytest.fixture
async def memory_seed_data(db_session):
    # Setup user
    user = User(email="test@example.com", full_name="Test User")
    db_session.add(user)
    await db_session.flush()
    
    # Setup organization and workspace
    org = Organization(name="Test Org", slug="test-org", owner_id=user.id)
    db_session.add(org)
    await db_session.flush()
    
    workspace = Workspace(name="Test WS", slug="test-ws", organization_id=org.id)
    db_session.add(workspace)
    await db_session.flush()
    
    # Create mock memory
    memory = IncidentMemory(
        incident_id="inc-memory-test-01",
        workspace_id=workspace.id,
        organization_id=workspace.organization_id,
        summary="Database latency spike in eu-west-1",
        severity="High",
        status="RESOLVED",
        confidence=0.95,
        time_taken_ms=120000,
        root_cause={"primary": "Missing index on users table"},
        recommended_fix={"actions": ["CREATE INDEX idx_users ON users(email)"]},
        generated_report={"title": "DB Outage"}
    )
    
    db_session.add(memory)
    await db_session.flush()
    
    tag1 = IncidentTag(memory_id=memory.id, name="service", value="database")
    tag2 = IncidentTag(memory_id=memory.id, name="environment", value="prod")
    db_session.add_all([tag1, tag2])
    
    await db_session.commit()
    return memory, workspace


@pytest.fixture
async def setup_test_workspace2(db_session):
    user = User(email="test2@example.com", full_name="Test User 2")
    db_session.add(user)
    await db_session.flush()

    org = Organization(name="Test Org 2", slug="test-org-2", owner_id=user.id)
    db_session.add(org)
    await db_session.flush()
    
    workspace = Workspace(name="Test WS 2", slug="test-ws-2", organization_id=org.id)
    db_session.add(workspace)
    await db_session.commit()
    return workspace


@pytest.mark.asyncio
async def test_get_memories(client: AsyncClient, memory_seed_data, admin_headers):
    memory, workspace = memory_seed_data
    
    response = await client.get(
        f"/api/v1/memory?workspace_id={workspace.id}", 
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["incident_id"] == "inc-memory-test-01"
    assert data[0]["summary"] == "Database latency spike in eu-west-1"
    assert len(data[0]["tags"]) == 2


@pytest.mark.asyncio
async def test_get_memory_by_id(client: AsyncClient, memory_seed_data, admin_headers):
    memory, workspace = memory_seed_data
    
    response = await client.get(
        f"/api/v1/memory/{memory.id}?workspace_id={workspace.id}", 
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == "inc-memory-test-01"
    assert data["severity"] == "High"


@pytest.mark.asyncio
async def test_search_similar_memories(client: AsyncClient, memory_seed_data, admin_headers):
    memory, workspace = memory_seed_data
    
    # Search for matching summary term
    response = await client.get(
        f"/api/v1/memory/search?workspace_id={workspace.id}&q=latency", 
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["incident_id"] == "inc-memory-test-01"
    
    # Search for non-matching term
    response_empty = await client.get(
        f"/api/v1/memory/search?workspace_id={workspace.id}&q=unrelated_search", 
        headers=admin_headers
    )
    assert response_empty.status_code == 200
    assert len(response_empty.json()) == 0


@pytest.mark.asyncio
async def test_memory_workspace_isolation(client: AsyncClient, memory_seed_data, setup_test_workspace2, admin_headers):
    memory, workspace1 = memory_seed_data
    workspace2 = setup_test_workspace2
    
    # workspace2 should not see workspace1's memory
    response = await client.get(
        f"/api/v1/memory?workspace_id={workspace2.id}", 
        headers=admin_headers
    )
    
    assert response.status_code == 200
    assert len(response.json()) == 0
