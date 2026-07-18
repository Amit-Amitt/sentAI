import uuid
from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sentinel_api.database.base import Base
from sentinel_api.database.session import get_db_session
from sentinel_api.database.seed import seed_roles_and_permissions
from sentinel_api.models.user import User


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture providing a clean in-memory SQLite database session with seeded roles."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

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
    """Fixture providing a test client."""
    app.dependency_overrides[get_db_session] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.asyncio
async def test_collaboration_and_invitations_flow(app: FastAPI, test_client: AsyncClient, db_session: AsyncSession):
    # 1. Create Organization (creates seed user as Owner)
    org_resp = await test_client.post(
        "/api/v1/organizations",
        json={"name": "Sentinel Org", "slug": "sentinel-org"},
    )
    assert org_resp.status_code == 201
    org = org_resp.json()
    org_id = org["id"]

    # 2. Get default workspace ID
    ws_resp = await test_client.get(f"/api/v1/organizations/{org_id}/workspaces")
    assert ws_resp.status_code == 200
    workspaces = ws_resp.json()["results"]
    default_ws_id = workspaces[0]["id"]

    # 3. Create a scoped invitation targeting the default workspace
    inv_resp = await test_client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={
            "email": "invitee@sentinel.com",
            "role": "engineer",
            "workspaces": [default_ws_id],
        },
    )
    assert inv_resp.status_code == 201
    inv = inv_resp.json()
    assert inv["email"] == "invitee@sentinel.com"
    assert inv["role"] == "engineer"
    assert inv["status"] == "pending"
    assert default_ws_id in inv["workspaces"]

    # Get invitation by token
    from sentinel_api.models.invitation import Invitation
    from sqlalchemy import select
    res = await db_session.execute(select(Invitation).where(Invitation.email == "invitee@sentinel.com"))
    db_inv = res.scalars().first()
    assert db_inv is not None
    real_token = db_inv.token

    # Retrieve invitation details publicly using the token
    details_resp = await test_client.get(f"/api/v1/invitations/{real_token}")
    assert details_resp.status_code == 200
    assert details_resp.json()["email"] == "invitee@sentinel.com"

    # 4. Create another user in DB to accept the invitation
    invitee_user = User(
        email="invitee@sentinel.com",
        full_name="Invitee User",
        is_active=True,
    )
    db_session.add(invitee_user)
    await db_session.flush()

    # Override get_current_user dependency to simulate invitee accepting the invitation
    from sentinel_api.api.v1.dependencies.current_user import get_current_user
    app.dependency_overrides[get_current_user] = lambda: invitee_user

    # Accept invitation
    accept_resp = await test_client.post(f"/api/v1/invitations/{real_token}/accept")
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "accepted"

    # Restore current user override to the original owner user (first user created in DB)
    res_owner = await db_session.execute(select(User).where(User.email == "admin@sentinel.ai"))
    owner_user = res_owner.scalars().first()
    app.dependency_overrides[get_current_user] = lambda: owner_user

    # 5. List members (should show Owner and the new accepted Engineer member)
    members_resp = await test_client.get(f"/api/v1/organizations/{org_id}/members")
    assert members_resp.status_code == 200
    members = members_resp.json()["results"]
    assert len(members) == 2
    
    engineer_member = next(m for m in members if m["role"] == "engineer")
    assert engineer_member["user"]["email"] == "invitee@sentinel.com"
    # Ensure they are added to the workspace too
    assert len(engineer_member["workspaces"]) == 1
    assert engineer_member["workspaces"][0]["id"] == default_ws_id

    # 6. Test Demote Owner Protection
    owner_member = next(m for m in members if m["role"] == "owner")
    demote_resp = await test_client.patch(
        f"/api/v1/organizations/{org_id}/members/{owner_member['id']}",
        json={"role": "admin"},
    )
    # Demoting Owner should be prohibited
    assert demote_resp.status_code == 400

    # 7. Test Ownership Transfer
    transfer_resp = await test_client.post(
        f"/api/v1/organizations/{org_id}/members/{engineer_member['id']}/transfer-ownership"
    )
    assert transfer_resp.status_code == 200
    assert transfer_resp.json()["role"] == "owner"

    # List members again to verify roles have swapped
    members_resp = await test_client.get(f"/api/v1/organizations/{org_id}/members")
    members = members_resp.json()["results"]
    
    new_owner = next(m for m in members if m["user"]["email"] == "invitee@sentinel.com")
    new_admin = next(m for m in members if m["user"]["email"] == "admin@sentinel.ai")
    assert new_owner["role"] == "owner"
    assert new_admin["role"] == "admin"

    # 8. Test Audit Logs Activity Logs
    act_resp = await test_client.get(f"/api/v1/organizations/{org_id}/activity")
    assert act_resp.status_code == 200
    activities = act_resp.json()["results"]
    assert len(activities) > 0
    actions = [a["action"] for a in activities]
    assert "ownership_transferred" in actions
    assert "invitation_accepted" in actions

    # Clean up overrides
    app.dependency_overrides.pop(get_current_user, None)
