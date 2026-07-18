import pytest
import hmac
import hashlib
import json
from sentinel_api.services.github_risk_analyzer import GithubRiskAnalyzer
from sentinel_api.api.v1.routers.github import verify_github_signature

def test_github_risk_analyzer_high_risk():
    files = ["src/main.py", "package.json", "docker-compose.yml", "alembic/versions/123_init.py"]
    score, factors = GithubRiskAnalyzer.analyze_risk(files)
    
    assert score >= 0.7  # (0.3 for config, 0.4 for migration)
    assert len(factors) == 2
    assert any("migration" in f.lower() for f in factors)
    assert any("configuration" in f.lower() for f in factors)

def test_github_risk_analyzer_low_risk():
    files = ["README.md", "src/utils.py"]
    score, factors = GithubRiskAnalyzer.analyze_risk(files)
    
    assert score == 0.0
    assert len(factors) == 0
    
def test_github_risk_analyzer_volume():
    # Create 55 mock files
    files = [f"src/file_{i}.py" for i in range(55)]
    score, factors = GithubRiskAnalyzer.analyze_risk(files)
    
    assert score == 0.4 # Volume > 50
    assert len(factors) == 1
    assert "High volume" in factors[0]

def test_verify_github_signature():
    secret = "my_super_secret"
    payload = json.dumps({"action": "opened"}).encode('utf-8')
    
    # Generate valid signature
    hash_object = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
    valid_signature = "sha256=" + hash_object.hexdigest()
    
    # Test valid
    assert verify_github_signature(payload, valid_signature, secret) is True
    
    # Test invalid
    assert verify_github_signature(payload, "sha256=invalidhash", secret) is False
    
    # Test missing
    assert verify_github_signature(payload, None, secret) is False
    assert verify_github_signature(payload, valid_signature, "") is False
