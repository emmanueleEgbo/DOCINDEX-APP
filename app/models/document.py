"""
Document ORM model.

Each row in the 'documents' table represents ONE CHUNK of an original document.
A single uploaded document may produce many rows (one per chunk).

Why store chunks as separate rows rather than embedding the full document?
  - The context window of the LLM is limited. We can only pass a few hundred
    tokens at a time as context.
  - Vector similarity search works best on focused, short pieces of text.
  - A 10-page document split into 20 chunks gives 20 searchable units.
    Storing it as one row gives only 1 (much less precise).

The 'source_document_id' field groups all chunks that belong to the same
original document — used for deletion and re-indexing.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class Document(Base):
    __tablename__="documents"

    id: Mapped[str] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Unique ID for this specific chunk row"
    )

    # ── Source document grouping ───────────────────────────────────────────────
    source_document_id = mapped_column(
        String(36),
        nullable=False,
        index=True,
        # All chunks from the same uploaded document share this UUID.
        # To delete an entire document: DELETE WHERE source_document_id = ?
        # To re-index a document: delete all rows with this ID, then re-insert.
        comment="UUID grouping all chunks of one uploaded document"
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Title of the original document"
    )

    source: Mapped[str] = mapped_column(
        String(200),
        nullable=True,
        index=True,
        comment="Where this document came from: e.g. 'support_docs', 'faq', 'manual'"
    )

    # ── Chunk data ────────────────────────────────────────────────────────────
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Position of this chunk within the original document (0-based)"
    )

    chunk_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Total number of chunks the original document was split into"
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="The actual text content of this chunk"
    )

    # ── The embedding vector ──────────────────────────────────────────────────
    embedding: Mapped[List[float] | None] = mapped_column(
        Vector(1536),
        nullable=True,
        # nullable=True: we insert the row first, then update with the embedding.
        # This lets us handle embedding API failures gracefully without losing
        # the chunk text.
        comment="1536-dimensional embedding vector from text-embedding-3-small"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )