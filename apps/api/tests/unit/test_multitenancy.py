import uuid
from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sentinel_api.database.base import Base
from sentinel_api.database.session import get_db_session
from sentinel_api.database.seed import seed_roles_and_permissions


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture providing a clean in-memory SQLite database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Import all models to ensure metadata is populated
    import sentinel_api.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_maker() as session:
        # Pre-seed roles and permissions
        await seed_roles_and_permissions(session)
        yield session
        await session.rollback()

    await engine.dispose()


@pytest.fixture
async def test_client(
    app: FastAPI, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """Fixture providing a test client with a real in-memory SQLite DB session."""
    app.dependency_overrides[get_db_session] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.asyncio
async def test_multitenancy_flow(test_client: AsyncClient):
    # 1. List organizations (should auto-create the seed user first, and return empty list)
    resp = await test_client.get("/api/v1/organizations")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert len(data["results"]) == 0

    # 2. Create organization
    payload = {
      "name": "Acme Corp",
      "slug": "acme-corp",
      "industry": "Technology",
      "region": "North America"
    }
    resp = await test_client.post("/api/v1/organizations", json=payload)
    assert resp.status_code == 201
    org = resp.json()
    assert org["name"] == "Acme Corp"
    assert org["slug"] == "acme-corp"
    assert org["id"] is not None

    org_id = org["id"]

    # 3. List organizations again (should have 1 organization now)
    resp = await test_client.get("/api/v1/organizations")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["results"][0]["id"] == org_id

    # 4. Get organization details
    resp = await test_client.get(f"/api/v1/organizations/{org_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Acme Corp"

    # 5. List workspaces (should have 1 default workspace auto-created)
    resp = await test_client.get(f"/api/v1/organizations/{org_id}/workspaces")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["results"][0]["slug"] == "default"

    # 6. Create workspace
    ws_payload = {
      "name": "Production",
      "slug": "production",
      "environment": "production",
      "description": "Acme production workspace"
    }
    resp = await test_client.post(f"/api/v1/organizations/{org_id}/workspaces", json=ws_payload)
    assert resp.status_code == 201
    ws = resp.json()
    assert ws["name"] == "Production"
    assert ws["slug"] == "production"
    assert ws["environment"] == "production"

    ws_id = ws["id"]

    # 7. List workspaces again (should have 2 now)
    resp = await test_client.get(f"/api/v1/organizations/{org_id}/workspaces")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2

    # 8. Get workspace by ID
    resp = await test_client.get(f"/api/v1/workspaces/{ws_id}")
    assert resp.status_code == 200
    assert resp.json()["slug"] == "production"

    # 9. List members (should contain the owner by default)
    resp = await test_client.get(f"/api/v1/organizations/{org_id}/members")
    assert resp.status_code == 200
    members = resp.json()
    assert members["total"] == 1
    assert members["results"][0]["role"] == "owner"

    # 10. Create an invitation
    inv_payload = {
      "email": "engineer@acme.com",
      "role": "engineer"
    }
    resp = await test_client.post(f"/api/v1/organizations/{org_id}/invitations", json=inv_payload)
    assert resp.status_code == 201
    inv = resp.json()
    assert inv["email"] == "engineer@acme.com"
    assert inv["role"] == "engineer"
    assert inv["status"] == "pending"

    # 11. List invitations
    resp = await test_client.get(f"/api/v1/organizations/{org_id}/invitations")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
