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
from app.core.database import engine, Base
from app.api.document_routes import document_router
from app.models import document  # noqa: F401