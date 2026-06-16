import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.query_schema import QueryRequest, QueryResponse
from app.schemas.document_schema import ErrorResponse
from app.services import query_service

logger = logging.getLogger(__name__)

query_router = APIRouter(prefix="/v1/query", tags=["query"])


@query_router.post(
    "",
    response_model=QueryResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        502: {"model": ErrorResponse, "description": "OpenAI API error"},
    },
    summary="Ask a question against indexed documents",
    description="""
    Send a plain text question. The pipeline runs automatically:
    1. Embeds the question using OpenAI (same model used during indexing)
    2. Finds the top K most similar chunks in pgvector using cosine similarity
    3. Passes the chunks as context to the LLM
    4. Returns the grounded answer + the source chunks used to generate it

    Index documents first via POST /v1/documents before querying.
    """,
)
async def query(
    body: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
   pass