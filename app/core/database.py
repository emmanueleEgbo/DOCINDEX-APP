"""
Async SQLAlchemy engine and session factory.
"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

class Base (DeclarativeBase):
    pass


async_engine = create_async_engine(
    settings.async_database_url,   # Set True during development to see SQL in the console
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True            # Test each connection before use (handles DB restarts)
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    # expire_on_commit=False: after db.commit(), objects keep their attribute values.
    # Without this, accessing doc.id after a commit would trigger another DB query.
)

# Fastapi Dependency
async def get_db():
    """
    Yields an AsyncSession for one request, then closes it automatically.
    Rolls back on any unhandled exception to keep the DB state clean.

    Usage in routes:
        async def my_route(db: AsyncSession = Depends(get_db)):
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as exc:
            await session.rollback()
            raise RuntimeError(str(exc))
