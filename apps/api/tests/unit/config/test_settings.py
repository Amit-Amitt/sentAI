import pytest
import os
from pydantic import ValidationError

# We cannot easily re-import and validate `settings` globally here because it is eagerly evaluated
# on module import. So we import the class directly to test initialization.
from sentinel_api.config.settings import Settings
from sentinel_api.config.utils import mask_secret

def test_mask_secret():
    assert mask_secret(None) == "*not set*"
    assert mask_secret("") == "*not set*"
    assert mask_secret("short") == "***"
    assert mask_secret("super_long_secret_string") == "sup***ing"

def test_settings_validation_failure():
    # If we pass nothing to Settings, it should try to read from the environment or fail
    # because of required fields like JWT_SECRET and DATABASE_URL.
    
    # Temporarily remove them from env if they exist to force a failure
    old_env = dict(os.environ)
    for key in list(os.environ.keys()):
        if key.startswith("SENTINEL_"):
            del os.environ[key]
            
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)
        
    errors = str(exc_info.value)
    assert "DATABASE_URL" in errors
    assert "JWT_SECRET" in errors
    assert "REDIS_URL" in errors
    
    # Restore env
    os.environ.clear()
    os.environ.update(old_env)

def test_settings_validation_success():
    # Provide the bare minimum required secrets
    cfg = Settings(
        DATABASE_URL="postgresql://user:pass@localhost/db",
        REDIS_URL="redis://localhost",
        JWT_SECRET="secret",
        AUTH_ENCRYPTION_KEY="secret2"
    )
    
    assert cfg.DATABASE_URL == "postgresql+psycopg://user:pass@localhost/db"
    assert cfg.ENABLE_AI is True # Default value
