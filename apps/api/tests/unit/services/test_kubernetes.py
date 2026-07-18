import pytest
from sentinel_api.services.kubernetes_client import KubernetesClient

def test_kubernetes_client_initialization_mock():
    # When kubernetes package is not available or cluster not found, it should fall back safely.
    client = KubernetesClient(in_cluster=False, kubeconfig_path="/tmp/nonexistent")
    
    assert client.initialized is False
    
    # Methods should return empty lists rather than crash
    assert client.list_nodes() == []
    assert client.list_pods() == []
    assert client.list_events() == []

# In a full test suite, we would use the `responses` or `mock` library to patch the kubernetes python client
# and inject fake Cluster Node and Pod payloads to verify the parsing logic.
