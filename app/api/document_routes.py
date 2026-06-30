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
    try:
        return await document_service.index_document(db, body)
    except ValueError as exc:
        # Raised by chunking_service when content is empty after cleaning
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except RuntimeError as exc:
        # Raised by embedding_service when the OpenAI API call fails
        logger.error("Indexing failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Embedding API error: {exc}",
        )


@document_router.post(
    "/upload",
    response_model=IndexingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": ErrorResponse, "description": "Unsupported file type or empty content"},
        502: {"model": ErrorResponse, "description": "Embedding API error"},
    },
    summary="Upload a file for indexing",
    description="""
    Upload a .txt, .pdf, or .docx file. The server extracts the text and runs
    the same indexing pipeline as POST /v1/documents.

    Form fields:
    - file   (required) — the file to upload
    - title  (optional) — defaults to the filename if not provided
    - source (optional) — e.g. 'faq', 'manual', 'hr_policy'
    """,
)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
) -> IndexingResponse:
    

@document_router.get(
    "",
    response_model=List[DocumentSummary],
    summary="List all indexed documents",
    description="""
    Returns one summary entry per uploaded document.
    Shows: source_document_id, title, source, chunk_count, created_at.
    Embedding vectors are never included in list responses.
    """
)
async def list_documents(
    db: AsyncSession = Depends(get_db),
) -> List[DocumentSummary]:
    return await document_service.get_all_documents(db)


@document_router.get(
    "/{source_document_id}",
    response_model=DocumentSummary,
    responses={404: {"model": ErrorResponse}},
    summary="Get one document's metadata",
)
async def get_document(
    source_document_id: str,
    db: AsyncSession = Depends(get_db),
) -> DocumentSummary:
    doc = await document_service.get_document_by_id(db, source_document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {source_document_id} not found",
        )
    return doc


@document_router.delete(
    "/{source_document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
    summary="Delete a document and all its chunks",
    description="""
    Deletes every chunk row with this source_document_id.
    This is a hard delete — all content and embeddings are permanently removed.
    To update a document: delete it, then re-POST with the updated content.
    """
)
async def delete_document(
    source_document_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await document_service.delete_document(db, source_document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {source_document_id} not found",
        )