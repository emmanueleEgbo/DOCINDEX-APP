"""
OpenAI chat completion — generates the final answer from context + question.

This is the last step of the RAG pipeline:
  1. Indexing half (done): documents → chunks → embeddings → stored in pgvector
  2. Query half (this file): question + retrieved chunks → LLM → answer
"""
import logging
from typing import List
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.openai_api_key)