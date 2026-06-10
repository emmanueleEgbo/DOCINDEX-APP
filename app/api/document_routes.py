"""
Document API routes.

Route handlers are intentionally thin:
  - Validate input (Pydantic handles this automatically)
  - Call the service
  - Return the response or raise HTTPException

All business logic and DB logic lives in services and repositories.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.document_schema import (
    DocumentCreate,
    DocumentSummary,
    IndexingResponse,
    ErrorResponse,
)
from app.services import document_service

logger = logging.getLogger(__name__)

document_router = APIRouter(prefix="/v1/documents", tags=["documents"])


@document_router.post(
    "",
    response_model=IndexingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Embedding or DB error"},
    },
    summary="Index a new document",
    description="""
    Accepts a document title and content.
    The pipeline runs automatically:
    1. Cleans and splits the content into chunks (~500 tokens, 50-token overlap)
    2. Embeds all chunks in a single batch OpenAI API call
    3. Stores all chunk rows + their embedding vectors in PostgreSQL (pgvector)

    Returns a source_document_id that groups all chunks.
    Use this ID to fetch or delete the document later.
    """
)
async def index_document(
    body: DocumentCreate,
    db: AsyncSession = Depends(get_db),
) -> IndexingResponse:
    pass