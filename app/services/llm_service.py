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

# The system prompt instructs the LLM to answer ONLY from the provided context.
# This prevents hallucination — the model cannot make up information.
SYSTEM_PROMPT = """\
You are a helpful assistant. Answer the user's question using ONLY the context provided below.
If the answer is not found in the context, say "I don't have enough information to answer that."
Do not make up information that is not in the context.

Context:
{context}"""