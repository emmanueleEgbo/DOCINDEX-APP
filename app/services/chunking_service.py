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
    text = re.sub(r'\s+', ' ', text)
    # Remove non-printable control characters (except spaces)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = None,
    overlap: int = None,
) -> List[str]:
    pass
