import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Verifies that the /health endpoint works and custom middlewares are executed."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"

    # Assert custom middlewares worked
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers
