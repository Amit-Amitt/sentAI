import jwt
from fastapi import HTTPException, status
from typing import Optional
from fastapi import Depends, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sentinel_api.services.identity_service import IdentityService

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[dict]:
    """Prepares support for API Key authentication validation."""
    if not api_key:
        return None
    # Real validation would verify `api_key` against ApiToken DB table
    return {"api_key": api_key}


async def get_current_user_jwt(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[dict]:
    """Validates JWT and extracts user ID."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = IdentityService.decode_jwt(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User identifier not found in token")
            
        return {"user_id": user_id, "scopes": payload.get("scopes", [])}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
