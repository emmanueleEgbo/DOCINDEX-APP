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