import pytest
from sentinel_api.services.identity_service import IdentityService

def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = IdentityService.hash_password(password)
    
    # Should not store plain text
    assert password != hashed
    
    # Should verify correctly
    assert IdentityService.verify_password(password, hashed) is True
    
    # Should reject incorrect password
    assert IdentityService.verify_password("WrongPassword123!", hashed) is False

def test_totp_generation():
    secret = IdentityService.generate_totp_secret()
    assert len(secret) == 32
    
    # Generate a code and immediately verify it
    import pyotp
    totp = pyotp.TOTP(secret)
    code = totp.now()
    
    assert IdentityService.verify_totp(secret, code) is True
    assert IdentityService.verify_totp(secret, "000000") is False

@pytest.mark.asyncio
async def test_jwt_lifecycle():
    user_id = "12345678-1234-5678-1234-567812345678"
    scopes = ["admin", "read"]
    
    # Needs SENTINEL_JWT_SECRET in env for this to work natively.
    # We will assume IdentityService relies on settings.JWT_SECRET
    import os
    if not os.environ.get("SENTINEL_JWT_SECRET"):
        pytest.skip("JWT Secret not set in environment, skipping")
        
    access, refresh = IdentityService.create_jwt_tokens(user_id, scopes)
    
    assert access is not None
    assert refresh is not None
    
    decoded = IdentityService.decode_jwt(access)
    assert decoded["sub"] == user_id
    assert decoded["type"] == "access"
    assert "admin" in decoded["scopes"]
