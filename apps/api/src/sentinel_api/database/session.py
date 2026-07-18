from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from sentinel_api.config.settings import settings
from sentinel_api.logging.logger import get_logger

logger = get_logger(__name__)

# Configure modern connection pooling for production readiness
engine_kwargs = {
    "echo": False,
    "pool_pre_ping": True,
}

# SQLite does not support pool_size and max_overflow in StaticPool / SingletonThreadPool
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update(
        {
            "pool_size": 20,
            "max_overflow": 10,
        }
    )

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Async generator to yield database sessions per request.

    Ensures rollback on error and proper closing of connection resources.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.exception(
                "Database session transaction failed; rolling back.", error=str(e)
            )
            raise
        finally:
            await session.close()
