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