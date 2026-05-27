"""
Async SQLAlchemy engine and session factory.
Pattern is identical to what was used in the URL shortener — async engine,
async_sessionmaker, get_db dependency injected via FastAPI Depends().
"""