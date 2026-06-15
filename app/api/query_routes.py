import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.query_schema import QueryRequest, QueryResponse
from app.schemas.document_schema import ErrorResponse
from app.services import query_service

logger = logging.getLogger(__name__)

query_router = APIRouter(prefix="/v1/query", tags=["query"])