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