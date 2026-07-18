import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete

from sentinel_api.database.session import engine
from sentinel_api.models.iam import UserSession, ApiToken

logger = structlog.get_logger("sentinel_api.workers.iam_tasks")

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def _cleanup_expired_sessions_async():
    """Delete revoked or expired sessions and API tokens."""
    async with AsyncSessionLocal() as db:
        now = datetime.datetime.utcnow()
        
        # 1. Cleanup Sessions
        stmt_sessions = delete(UserSession).where(UserSession.expires_at < now)
        res_sessions = await db.execute(stmt_sessions)
        
        # 2. Cleanup Revoked API Tokens (expired tokens usually kept for audit, revoked are purged)
        stmt_tokens = delete(ApiToken).where(ApiToken.is_revoked == True)
        res_tokens = await db.execute(stmt_tokens)
        
        await db.commit()
        
        logger.info(
            "IAM Cleanup Complete", 
            expired_sessions_removed=res_sessions.rowcount,
            revoked_tokens_removed=res_tokens.rowcount
        )

def cleanup_expired_sessions():
    import asyncio
    asyncio.run(_cleanup_expired_sessions_async())
