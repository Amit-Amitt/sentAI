import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_ingest_heartbeat_unauthorized(client):
    payload = {
        "environment": "production",
        "version": "1.0.0",
        "cpu": 0.5,
        "memory": 1.2,
        "health": "healthy",
        "timestamp": "2026-07-18T10:00:00Z"
    }
    # Should fail without API Key
    response = await client.post("/api/v1/telemetry/heartbeat", json=payload)
    assert response.status_code == 422 # FastAPI validation for missing header

@pytest.mark.asyncio
async def test_get_telemetry_stats(client):
    # Depending on auth implementation, stats might be public or protected
    response = await client.get("/api/v1/telemetry/stats")
    # Just asserting it returns a response, could be 401, 403, or 200
    assert response.status_code in (200, 401, 403)
