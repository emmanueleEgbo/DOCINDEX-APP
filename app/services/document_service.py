"""
Indexing pipeline orchestrator.

This service connects the three steps:
  1. Chunk the document (chunking_service)
  2. Embed all chunks in one batch call (embedding_service)
  3. Store chunks + embeddings in PostgreSQL (document_repository)

It is called by the route handler. The route handler knows nothing
about chunking or embeddings — that is all in here.
"""
import uuid
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chunking_service import prepare_document
from app.services.embedding_service import embed_batch
from app.repositories.document_repository import DocumentRepository
from app.models.document import Document
from app.schemas.document_schema import DocumentCreate, DocumentSummary, IndexingResponse

logger = logging.getLogger(__name__)


async def index_document(
    db: AsyncSession,
    data: DocumentCreate,
) -> IndexingResponse:
    """
    Full indexing pipeline for one uploaded document.

    Steps:
      1. Generate a shared UUID for all chunks of this document
      2. Clean and split the content into chunks
      3. Embed all chunks in one batch API call
      4. Store each chunk + its embedding in PostgreSQL
      5. Return a summary of what was indexed

    Args:
        db:   Async database session (injected by FastAPI).
        data: Validated request body with title, content, source.

    Returns:
        IndexingResponse with chunk_count and the source_document_id.
    """
    pass