"""
Fixed-size chunking with overlap.

Chunking is character-based here for simplicity.
  1 token ≈ 4 characters (English text).
  chunk_size = 500 tokens → 500 x 4 = 2,000 characters per chunk.
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
    """
    Split text into overlapping fixed-size chunks.

    Args:
        text:       The cleaned text to split.
        chunk_size: Approximate chunk size in tokens (default from settings).
        overlap:    Overlap in tokens between adjacent chunks (default from settings).

    Returns:
        A list of text strings, each approximately chunk_size tokens long.

    Example with chunk_size=4 tokens, overlap=1 token (for illustration):
        text = "The quick brown fox jumps over the lazy dog"
        chunks = [
            "The quick brown fox",          ← tokens 0-3
            "fox jumps over the",           ← tokens 3-6  (fox is the overlap)
            "the lazy dog",                 ← tokens 6-8
        ]
    """
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    # Convert token counts to character counts
    chars_per_chunk   = chunk_size  * 4
    chars_per_overlap = overlap     * 4
    step              = chars_per_chunk - chars_per_overlap

    
    if step <= 0:
        raise ValueError(
            f"overlap ({overlap}) must be less than chunk_size ({chunk_size})"
        )
    
    chunks = []
    start = 0

    while start < len(text):
        end   = start + chars_per_chunk
        chunk = text[start:end].strip()

        if chunk:  
            chunks.append(chunk)

        start += step

    return chunks


def prepare_document(
    text: str,
    chunk_size: int = None,
    overlap: int = None,
) -> List[str]:
    """
    Clean and chunk a document in one call.
    This is the function called by the indexing service.
    """
    cleaned = clean_text(text)

    if not cleaned:
        raise ValueError("Document is empty after cleaning")

    return chunk_text(cleaned, chunk_size=chunk_size, overlap=overlap)
