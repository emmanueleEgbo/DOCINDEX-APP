"""
FastAPI application entry point.

The lifespan context manager handles startup and shutdown:
  Startup:  create DB tables, enable pgvector extension
  Shutdown: dispose the connection pool cleanly

Run with:
    uvicorn app.main:app --reload
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from app.core.database import async_engine, Base
from app.api.document_routes import document_router
from app.models import document  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up DocMind API...")
    async with async_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        logger.info("pgvector extension enabled")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")
    yield
    logger.info("Shutting down DocMind API...")
    await async_engine.dispose()
 

app = FastAPI(
    title="DocMind API",
    description="AI-powered document indexing and retrieval backend. "
                "Upload documents, search by meaning, get grounded answers.",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(document_router)

@app.get("/", tags=["root"])
async def root():
    return {
        "service": "DocMind API",
        "version": "1.0.0",
        "docs": "/docs",
    }