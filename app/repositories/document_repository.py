"""
All database operations for the Document model.

The repository pattern keeps DB queries out of route handlers and services.
Services call the repository. Routes call services. Nothing leaks.
"""
import logging
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, delete, func, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document_schema import DocumentSummary

logger = logging.getLogger(__name__)


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chunks(
        self,
        source_document_id: str,
        title: str,
        source: Optional[str],
        chunks: List[str],
        embeddings: List[List[float]],
    ) -> List[Document]:
        """
        Insert all chunk rows for one document in a single transaction.

        Why a single transaction?
          Either ALL chunks are saved, or NONE are.
          If the process crashes after saving chunk 5 of 20, we don't want
          a partially-indexed document that can never be fully queried.
          The transaction rolls back on failure — clean state maintained.
        """
        documents = []

        for i, (chunk_text, embedding_vector) in enumerate(zip(chunks, embeddings)):
            doc = Document(
                source_document_id=source_document_id,
                title=title,
                source=source,
                chunk_index=i,
                chunk_total=len(chunks),
                content=chunk_text,
                embedding=embedding_vector,
            )
            self.db.add(doc)
            documents.append(doc)

        # commit only after all rows are successfully save atomically
        await self.db.commit()

        
        # Refresh all objects to load server-generated values (id, created_at)
        for doc in documents:
            await self.db.refresh(doc)

        logger.info(
            "Committed %d chunk rows for source_document_id=%s",
            len(documents), source_document_id
        )
        return documents
    

    async def get_document_summaries(self) -> List[DocumentSummary]:
        """
        Return one summary per source_document_id.

        Rather than returning all N chunk rows, we GROUP BY source_document_id
        and return: title, source, chunk_count, and the earliest created_at.

        This is what GET /v1/documents returns to the client.
        """
        result = await self.db.execute(
            select(
                Document.source_document_id,
                Document.title,
                Document.source,
                func.count(Document.id).label("chunk_count"),
                func.min(Document.created_at).label("created_at"),
            )
            .group_by(
                Document.source_document_id,
                Document.title,
                Document.source,
            )
            .order_by(func.min(Document.created_at).desc())
        )
        rows = result.all()

        return [
            DocumentSummary(
                source_document_id=row.source_document_id,
                title=row.title,
                source=row.source,
                chunk_count=row.chunk_count,
                created_at=row.created_at,
            )
            for row in rows
        ]
            
    async def get_summary_by_id(
        self, source_document_id: str
    ) -> Optional[DocumentSummary]:
        """Fetch one document's summary by its source_document_id."""
        pass
        result = await self.db.execute(
            select(
                Document.source_document_id,
                Document.title,
                Document.source,
                func.count(Document.id).label("chunk_count"),
                func.min(Document.created_at).label("created_at"),
            )
            .where(Document.source_document_id == source_document_id)
            .group_by(
                Document.source_document_id,
                Document.title,
                Document.source,
            )
        )

        row = result.one_or_none()

        if not row:
            return None

        return DocumentSummary(
            source_document_id=row.source_document_id,
            title=row.title,
            source=row.source,
            chunk_count=row.chunk_count,
            created_at=row.created_at,
        )
    
    async def delete_by_source_id(self, source_document_id: str) -> bool:
        """
        Delete ALL chunk rows with this source_document_id.

        This is a hard delete — all chunks gone in one statement.
        Called when a user deletes a document or when re-indexing
        (delete old chunks, then insert new ones).
        """
        result = await self.db.execute(
            delete(Document).where(
                Document.source_document_id == source_document_id
            )
        )
        await self.db.commit()

        deleted_count = result.rowcount
        logger.info(
            "Deleted %d chunk rows for source_document_id=%s",
            deleted_count, source_document_id
        )
        return deleted_count > 0
    

    async def search_similar_chunks(
        self,
        query_vector: List[float],
        top_k: int = 5,
    ) -> list:
        """
        Find the top_k chunks whose embedding is closest to the query_vector.

        Uses pgvector's <=> operator which computes cosine distance.
        Cosine distance = 1 - cosine similarity, so ordering by <=> ascending
        gives the most similar chunks first.

        The similarity score returned is: 1 - cosine_distance
        A score of 1.0 means identical, 0.0 means completely unrelated.
        """
        # pgvector expects the vector as a string: '[0.1, 0.2, ...]'
        vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"