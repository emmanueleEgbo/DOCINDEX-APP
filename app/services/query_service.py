"""
Query pipeline orchestrator — the retrieval half of RAG.

Steps:
  1. Embed the user's question (same model used during indexing)
  2. Search pgvector for the most similar chunks (cosine similarity)
  3. Pass the retrieved chunks + question to the LLM
  4. Return the answer with source citations
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.embedding_service import embed_text
from app.services.llm_service import generate_answer
from app.repositories.document_repository import DocumentRepository
from app.schemas.query_schema import QueryRequest, QueryResponse, SourceChunk

logger = logging.getLogger(__name__)


async def query_documents(
    db: AsyncSession,
    request: QueryRequest,
) -> QueryResponse:
    # Step 1: embed the question into a vector using the same OpenAI model
    # used during indexing — this ensures the vectors are in the same space
    logger.info("Embedding question: '%s'", request.question[:60])
    query_vector = await embed_text(request.question)

    # Step 2: find the top_k most similar chunks in pgvector
    repo = DocumentRepository(db)
    rows = await repo.search_similar_chunks(query_vector, top_k=request.top_k)

    # If the database is empty or no relevant chunks exist, return early
    if not rows:
        return QueryResponse(
            question=request.question,
            answer="I don't have enough information to answer that.",
            sources=[],
        )