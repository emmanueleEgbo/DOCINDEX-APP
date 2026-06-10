"""
FastAPI application entry point.

The lifespan context manager handles startup and shutdown:
  Startup:  create DB tables, enable pgvector extension
  Shutdown: dispose the connection pool cleanly

Run with:
    uvicorn app.main:app --reload
"""