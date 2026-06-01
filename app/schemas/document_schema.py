"""
Pydantic schemas define the shape of data in and out of the API.

Three clear separations:
  - DocumentCreate:   what the client sends in the request body
  - ChunkResponse:    one chunk row (no embedding — it's huge and not useful to clients)
  - DocumentResponse: summary of a full document (groups chunks)
  - DocumentDetail:   one document's metadata + its chunk count
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class DocumentCreate(BaseModel):
    """
    What client send when uploading a document.
    """
    title: str
    content: str
    source: Optional[str] = None   # e.g. "faq", "support", "product_manual"

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content cannot be empty")
        return v.strip()

    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title cannot be empty")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Nexora Refund Policy",
                "content": "Refunds are processed within 14 business days of the request...",
                "source": "support_docs"
            }
        }
    }


class ChunkResponse(BaseModel):
    """
    Response shape for a single chunk row.
    The embedding field is intentionally excluded — it is 1,536 numbers
    and completely useless to the API client.
    """
    id: int
    source_document_id: str
    title: str
    source: Optional[str]
    chunk_index: int
    chunk_total: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
    # from_attributes=True allows Pydantic to read values from SQLAlchemy model
    # objects directly (instead of needing a dict)


class DocumentSummary(BaseModel):
    """
    High-level summary of one uploaded document.
    Returned in the GET /v1/documents list.
    Groups all chunks under one entry so the client sees one document,
    not N individual chunk rows.
    """
    source_document_id: str
    title: str
    source: Optional[str]
    chunk_count: int       # How many chunks this document was split into
    created_at: datetime   # Timestamp of the first chunk (= when the doc was indexed)


class IndexingResponse(BaseModel):
    """
    Returned after POST /v1/documents completes successfully.
    """
    source_document_id: str
    title: str
    chunk_count: int
    message: str



class ErrorResponse(BaseModel):
    """
    Consistent error shape for all 4xx and 5xx responses.
    """
    code: str
    message: str