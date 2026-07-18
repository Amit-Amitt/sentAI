import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from sentinel_api.database.session import get_db_session
from sentinel_api.models.user import User
from sentinel_api.models.iam import UserSession
from sentinel_api.services.identity_service import IdentityService
from sentinel_api.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginResponse(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    mfa_required: bool = False
    mfa_session_id: Optional[str] = None

class MfaVerifyRequest(BaseModel):
    mfa_session_id: str
    code: str

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    """Standard OAuth2 Login Endpoint."""
    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.hashed_password:
        await AuditService.log_event("user.login", "failure", metadata={"email": form_data.username})
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    if not IdentityService.verify_password(form_data.password, user.hashed_password):
        await AuditService.log_event("user.login", "failure", user_id=str(user.id))
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    if user.mfa_enabled:
        # Generate a short-lived temp token to pass to the MFA verify endpoint
        # Here we just mock it for architecture demonstration
        mfa_session = str(uuid.uuid4())
        return LoginResponse(mfa_required=True, mfa_session_id=mfa_session)
        
    access_token, refresh_token = IdentityService.create_jwt_tokens(str(user.id))
    
    await AuditService.log_event("user.login", "success", user_id=str(user.id))
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/mfa/verify", response_model=LoginResponse)
async def verify_mfa(
    payload: MfaVerifyRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Verifies a TOTP code after initial login."""
    # In a full implementation, mfa_session_id would decrypt to the user_id via Redis
    # For now, this is architecturally stubbed.
    raise HTTPException(status_code=501, detail="Not fully implemented")
