import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel_api.database.session import get_db_session
from sentinel_api.models.iam import AuditLog, UserSession, SystemRole
from sentinel_api.api.v1.dependencies.security import get_current_user_jwt

router = APIRouter(prefix="/iam", tags=["iam"])

@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 50,
    current_user: dict = Depends(get_current_user_jwt),
    db: AsyncSession = Depends(get_db_session)
):
    """Fetch immutable audit logs. Requires Admin RBAC in production."""
    stmt = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit)
    res = await db.execute(stmt)
    return {"audit_logs": res.scalars().all()}

@router.get("/sessions")
async def get_active_sessions(
    current_user: dict = Depends(get_current_user_jwt),
    db: AsyncSession = Depends(get_db_session)
):
    """Fetch active sessions for the current user."""
    stmt = select(UserSession).where(
        UserSession.user_id == uuid.UUID(current_user["user_id"]),
        UserSession.is_revoked == False
    )
    res = await db.execute(stmt)
    return {"sessions": res.scalars().all()}

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: dict = Depends(get_current_user_jwt),
    db: AsyncSession = Depends(get_db_session)
):
    """Revoke a specific session, forcing the user to log in again."""
    session = await db.get(UserSession, uuid.UUID(session_id))
    if not session or str(session.user_id) != current_user["user_id"]:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.is_revoked = True
    await db.commit()
    return {"success": True}
