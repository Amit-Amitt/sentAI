from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.database.session import get_db_session


async def get_db(session: AsyncSession = Depends(get_db_session)) -> AsyncSession:
    """FastAPI dependency to retrieve the request-scoped database session."""
    return session
