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
    settings.async_database_url,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)