import uuid
from typing import AsyncGenerator
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sentinel_api.database.base import Base
from sentinel_api.database.session import get_db_session
from sentinel_api.database.seed import seed_roles_and_permissions
from sentinel_api.models.api_key import ApiKey, ApiKeyAudit, ApiKeyUsage, ApiKeyPermission
from sentinel_api.models.workspace import Workspace
from sentinel_api.models.organization import Organization


class MockSessionContext:
    """Mock context manager to route middleware DB calls to the test DB session."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Let the test fixture clean up the session
        pass


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
        await seed_roles_and_permissions(session)
        yield session
        await session.rollback()

    await engine.dispose()


@pytest.fixture
async def test_client(
    app: FastAPI, db_session: AsyncSession
) -> AsyncGenerator[AsyncClient, None]:
    """Fixture providing a test client with a real in-memory SQLite DB session."""
    from sentinel_api.middleware import security
    original_session_local = security.AsyncSessionLocal
    security.AsyncSessionLocal = lambda: MockSessionContext(db_session)

    app.dependency_overrides[get_db_session] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db_session, None)
    security.AsyncSessionLocal = original_session_local


@pytest.fixture
async def setup_test_workspace(db_session: AsyncSession):
    """Sets up a test organization and workspace in the DB."""
    # Create Organization
    org = Organization(
        name="Test Org",
        slug="test-org",
        owner_id=uuid.uuid4(),
    )
    db_session.add(org)
    await db_session.flush()

    # Create Workspace
    ws = Workspace(
        name="Development Workspace",
        slug="dev-ws",
        environment="development",
        organization_id=org.id,
    )
    db_session.add(ws)
    await db_session.flush()
    await db_session.commit()
    return org, ws


@pytest.mark.asyncio
async def test_api_key_lifecycle(test_client: AsyncClient, db_session: AsyncSession, setup_test_workspace):
    _, ws = setup_test_workspace
    ws_id = str(ws.id)

    # 1. Create API Key
    payload = {
        "name": "Integration CLI Key",
        "environment": "development",
        "scopes": ["incidents:read", "incidents:write", "logs:upload"],
        "description": "Used in GitHub Actions CI pipeline",
    }
    resp = await test_client.post(f"/api/v1/apikeys?workspace_id={ws_id}", json=payload)
    assert resp.status_code == 201
    key_data = resp.json()
    assert key_data["name"] == "Integration CLI Key"
    assert key_data["environment"] == "development"
    assert key_data["status"] == "active"
    assert "secret" in key_data
    assert key_data["secret"].startswith("sent_test_")
    assert key_data["prefix"].startswith("sent_test_")
    assert len(key_data["scopes"]) == 3

    key_id = key_data["id"]
    raw_secret = key_data["secret"]

    # 2. Get API Key list
    list_resp = await test_client.get(f"/api/v1/apikeys?workspace_id={ws_id}")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] == 1
    assert list_data["results"][0]["id"] == key_id
    assert "secret" not in list_data["results"][0]  # Verify secret is hidden in listings

    detail_resp = await test_client.get(f"/api/v1/apikeys/{key_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == key_id
    assert detail_data["workspace_id"] == ws_id

    copy_resp = await test_client.post(f"/api/v1/apikeys/{key_id}/copy")
    assert copy_resp.status_code == 200

    # 3. Update API Key properties
    update_payload = {
        "name": "Updated GitHub Actions Key",
        "scopes": ["incidents:read", "logs:upload"],
        "description": "Updated description",
    }
    patch_resp = await test_client.patch(f"/api/v1/apikeys/{key_id}", json=update_payload)
    assert patch_resp.status_code == 200
    updated_data = patch_resp.json()
    assert updated_data["name"] == "Updated GitHub Actions Key"
    assert updated_data["scopes"] == ["incidents:read", "logs:upload"]
    assert updated_data["description"] == "Updated description"

    # 4. Rotate API Key
    rotate_resp = await test_client.post(f"/api/v1/apikeys/{key_id}/rotate")
    assert rotate_resp.status_code == 200
    rotated_data = rotate_resp.json()
    assert rotated_data["id"] == key_id
    assert "secret" in rotated_data
    assert rotated_data["secret"] != raw_secret
    new_raw_secret = rotated_data["secret"]

    # 5. Get Usage Stats (should be empty initially)
    usage_resp = await test_client.get(f"/api/v1/apikeys/{key_id}/usage")
    assert usage_resp.status_code == 200
    usage_data = usage_resp.json()
    assert usage_data["requests_today"] == 0
    assert usage_data["requests_this_month"] == 0
    assert usage_data["failed_requests"] == 0
    assert usage_data["successful_requests"] == 0
    assert len(usage_data["audit_history"]) >= 3  # created, scope_changed, rotated

    audits_resp = await test_client.get(f"/api/v1/apikeys/{key_id}/audits")
    assert audits_resp.status_code == 200
    audits_data = audits_resp.json()
    assert audits_data["total"] >= 4

    # 6. Test Key Authentication Middleware & Scope Verification
    # Call an endpoint with the old rotated secret (should be unauthorized)
    incident_resp = await test_client.get(
        "/api/v1/incidents",
        headers={"X-API-Key": raw_secret, "X-Workspace-ID": ws_id}
    )
    assert incident_resp.status_code == 401

    # Call with the new rotated secret (valid, has incident:read scope)
    incident_resp_new = await test_client.get(
        "/api/v1/incidents",
        headers={"X-API-Key": new_raw_secret, "X-Workspace-ID": ws_id}
    )
    # The route returns 200 list_investigations
    assert incident_resp_new.status_code == 200

    # Call with mismatched Workspace ID
    mismatched_ws_id = str(uuid.uuid4())
    incident_resp_mismatch = await test_client.get(
        "/api/v1/incidents",
        headers={"X-API-Key": new_raw_secret, "X-Workspace-ID": mismatched_ws_id}
    )
    assert incident_resp_mismatch.status_code == 403

    # Call a route requiring scopes we don't have, e.g., POST incidents/analyze (requires incident:write)
    # We updated scopes to: ["incidents:read", "logs:upload"] (no incidents:write!)
    analyze_payload = {
        "incident_id": "test-inc-1",
        "severity": "P1",
        "status": "open",
        "summary": "Database connection timeout",
    }
    analyze_resp = await test_client.post(
        "/api/v1/incidents/analyze",
        json=analyze_payload,
        headers={"X-API-Key": new_raw_secret, "X-Workspace-ID": ws_id}
    )
    assert analyze_resp.status_code == 403  # Insufficient Scope

    # 7. Verify Usage Statistics incremented
    stats_resp = await test_client.get(f"/api/v1/apikeys/{key_id}/usage")
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert stats_data["requests_today"] >= 2  # The 200 OK + 403 Forbidden attempts
    assert len(stats_data["recent_usages"]) >= 2

    # 8. Revoke Key
    revoke_resp = await test_client.post(f"/api/v1/apikeys/{key_id}/revoke")
    assert revoke_resp.status_code == 200
    assert revoke_resp.json()["status"] == "revoked"

    # Verify key fails authentication after revocation
    revoked_auth_resp = await test_client.get(
        "/api/v1/incidents",
        headers={"X-API-Key": new_raw_secret, "X-Workspace-ID": ws_id}
    )
    assert revoked_auth_resp.status_code == 401

    # 9. Delete API Key
    delete_resp = await test_client.delete(f"/api/v1/apikeys/{key_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["success"] is True

    # Verify key is completely deleted
    list_after_delete = await test_client.get(f"/api/v1/apikeys?workspace_id={ws_id}")
    assert list_after_delete.json()["total"] == 0
