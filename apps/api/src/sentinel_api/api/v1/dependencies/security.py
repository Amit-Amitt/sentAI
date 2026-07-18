from typing import Optional
from fastapi import Depends, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_current_user_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[dict]:
    """Prepares support for API Key authentication validation."""
    if not api_key:
        return None
    return {"api_key": api_key}


async def get_current_user_jwt(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[dict]:
    """Prepares support for JWT/OAuth authentication token validation."""
    if not token:
        return None
    return {"token": token}
