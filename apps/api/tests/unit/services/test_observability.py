import pytest
from sentinel_api.services.observability_clients import BaseObservabilityClient

def test_base_observability_client_headers():
    # Test None auth
    client = BaseObservabilityClient("http://example.com")
    assert "Authorization" not in client.headers
    
    # Test Bearer auth
    client_bearer = BaseObservabilityClient("http://example.com", auth_method="bearer", credentials={"token": "test-token"})
    assert client_bearer.headers["Authorization"] == "Bearer test-token"
    
    # Test Basic auth
    client_basic = BaseObservabilityClient("http://example.com", auth_method="basic", credentials={"username": "usr", "password": "pwd"})
    # "usr:pwd" base64 is "dXNyOnB3ZA=="
    assert client_basic.headers["Authorization"] == "Basic dXNyOnB3ZA=="

# In a full test suite, we would mock the httpx library and assert the correct URLs are hit for
# Prometheus, Grafana, Loki, and Alertmanager clients.
