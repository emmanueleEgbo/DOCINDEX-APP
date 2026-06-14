from pydantic import BaseModel, field_validator
from typing import Optional, List


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5    # how many chunks to retrieve; default is 5

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("question cannot be empty")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "What is the refund policy?",
                "top_k": 5,
            }
        }
    }


class SourceChunk(BaseModel):
    """One chunk that was retrieved and used as context for the answer."""
    title: str
    source: Optional[str]
    content: str
    similarity: float  # cosine similarity score between 0 and 1


