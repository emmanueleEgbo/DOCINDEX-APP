"""
Fixed-size chunking with overlap.

Chunking is character-based here for simplicity.
  1 token ≈ 4 characters (English text).
  chunk_size=500 tokens → 500 x 4 = 2,000 characters per chunk.
  chunk_overlap=50 tokens → 50 x 4 = 200 characters of overlap.
"""
import re
from typing import List
from app.core.config import settings


def clean_text(text: str) -> str:
    """
    Normalise whitespace and remove control characters.
    A clean document produces cleaner embeddings.
    """