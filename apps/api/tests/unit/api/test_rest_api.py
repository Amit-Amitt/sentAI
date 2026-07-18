import pytest
import uuid
from httpx import AsyncClient
from fastapi import FastAPI
from sentinel_api.database.session import AsyncSessionLocal, get_db_session


@pytest.fixture(autouse=True)
async def use_real_db(app: FastAPI):
    """Overrides the mocked database session with a real SQLite in-memory session."""
    from sentinel_api.database.base import Base
    from sentinel_api.database.session import engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _get_real_db():
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db_session] = _get_real_db
    yield
    app.dependency_overrides.pop(get_db_session, None)


@pytest.mark.anyio
async def test_health_endpoint(client: AsyncClient):
    """Verifies that GET /health returns version and status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


@pytest.mark.anyio
async def test_analyze_incident_and_retrieve(client: AsyncClient):
    """Verifies submit, retrieve, list, and delete workflow."""
    analyze_payload = {
        "incident_id": "INC-889",
        "severity": "SEV1",
        "status": "active",
        "summary": "High latency on payment checkout flow",
        "logs": "Timeout connection error to DB",
        "metrics": "latency > 2.5s",
        "deployment_history": "Deployed version v1.2.3",
        "customer_reports": "Checkout returns error code 500",
    }

    # 1. Analyze Incident
    response = await client.post("/api/v1/incidents/analyze", json=analyze_payload)
    assert response.status_code == 202
    res_data = response.json()
    assert res_data["incident_id"] == "INC-889"
    assert "investigation_id" in res_data
    inv_id = res_data["investigation_id"]

    # 2. Get Incident Report by UUID
    response = await client.get(f"/api/v1/incidents/{inv_id}")
    assert response.status_code == 200
    report_data = response.json()
    assert report_data["metadata"]["incident_id"] == "INC-889"

    # 3. Get Incident Report by String incident_id
    response = await client.get("/api/v1/incidents/INC-889")
    assert response.status_code == 200
    report_data_2 = response.json()
    assert report_data_2["metadata"]["incident_id"] == "INC-889"

    # 4. Get Unified Report
    response = await client.get(f"/api/v1/reports/{inv_id}")
    assert response.status_code == 200
    unified_report = response.json()
    assert "executive_summary" in unified_report

    # 5. List Investigations (filtering/pagination)
    response = await client.get("/api/v1/incidents", params={"limit": 5, "skip": 0})
    assert response.status_code == 200
    list_data = response.json()
    assert list_data["total"] >= 1
    assert any(x["incident_id"] == "INC-889" for x in list_data["results"])

    # 6. Delete Investigation
    response = await client.delete(f"/api/v1/incidents/{inv_id}")
    assert response.status_code == 200
    del_data = response.json()
    assert del_data["success"] is True

    # 7. Check Not Found (404)
    response = await client.get(f"/api/v1/incidents/{inv_id}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_coordinator_run(client: AsyncClient):
    """Verifies manual coordinator execution route."""
    coordinator_payload = {
        "incident_context": {
            "incident_id": "INC-COORD-MAN",
            "severity": "SEV2",
            "status": "active",
            "summary": "Coordinator manual test run",
        },
        "execution_context": {"request_id": "req-man-1", "correlation_id": "corr-man-1"},
    }
    response = await client.post("/api/v1/coordinator/run", json=coordinator_payload)
    assert response.status_code == 200
    data = response.json()
    assert "agent_results" in data
    assert "Coordinator manual test run" in data["incident_summary"]


@pytest.mark.anyio
async def test_single_agent_endpoints(client: AsyncClient):
    """Verifies that sub-agents can be run independently."""
    agent_payload = {
        "incident_context": {
            "incident_id": "INC-AGENT-TEST",
            "severity": "SEV2",
            "status": "active",
            "summary": "Single agent run check",
            "signals": {
                "logs": "Timeout error connection refused",
                "metrics": "db_connections_active_count 40",
            },
        },
        "execution_context": {"request_id": "req-ag-1", "correlation_id": "corr-ag-1"},
    }

    # Log Agent Run
    response = await client.post("/api/v1/agents/log", json=agent_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["metadata"]["agent_name"] == "Log Agent"

    # Validation Error Check (400 AIPlatformException)
    invalid_payload = {
        "incident_context": {"signals": {}},
        "execution_context": {},
    }
    response = await client.post("/api/v1/agents/log", json=invalid_payload)
    assert response.status_code == 400
    err_data = response.json()
    assert err_data["success"] is False
    assert err_data["error_code"] == "AI_PLATFORM_ERROR"
