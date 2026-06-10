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
    # ── Step 1: Generate document ID ──────────────────────────────────────────
    # All chunks from this document share this ID.
    # Used later to delete or re-index the full document.
    source_document_id = str(uuid.uuid4())
    logger.info(
        "Starting indexing for document '%s' (id: %s)",
        data.title, source_document_id
    )

    # ── Step 2: Clean and chunk ───────────────────────────────────────────────
    chunks = prepare_document(data.content)
    chunk_total = len(chunks)
    logger.info("Document split into %d chunks", chunk_total)

    # ── Step 3: Batch embed all chunks ────────────────────────────────────────
    # All chunks are sent in ONE API call (or a few if > 100 chunks).
    # Much faster and cheaper than one call per chunk.
    logger.info("Requesting embeddings for %d chunks...", chunk_total)
    embeddings = await embed_batch(chunks)
    # embeddings[i] corresponds to chunks[i] — same order guaranteed
    
    
    # ── Step 4: Store all chunks in PostgreSQL ────────────────────────────────
    repo = DocumentRepository(db)
    documents = await repo.create_chunks(
        source_document_id=source_document_id,
        title=data.title,
        source=data.source,
        chunks=chunks,
        embeddings=embeddings,
    )
    logger.info(
        "Stored %d chunk rows for document '%s'",
        len(documents), data.title
    )

    # ── Step 5: Return summary ────────────────────────────────────────────────
    return IndexingResponse(
        source_document_id=source_document_id,
        title=data.title,
        chunk_count=chunk_total,
        message=f"Document indexed successfully into {chunk_total} chunks."
    )


async def get_all_documents(db: AsyncSession) -> List[DocumentSummary]:
    """
    Return a deduplicated list of documents (one entry per source_document_id).
    Clients see one document, not N chunk rows.
    """
    repo = DocumentRepository(db)
    return repo.get_document_summaries()


async def get_document_by_id(
    db: AsyncSession,
    source_document_id: str,
) -> Optional[DocumentSummary]:
    """Fetch metadata for one document by its source_document_id."""
    repo = DocumentRepository(db)
    return repo.get_summary_by_id(source_document_id)


async def delete_document(
    db: AsyncSession,
    source_document_id: str,
) -> bool:
    """
    Delete all chunk rows belonging to this source_document_id.
    Returns True if rows were deleted, False if not found.
    """
    repo = DocumentRepository(db)
    return repo.delete_by_source_id(source_document_id)