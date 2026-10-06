from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    content: str
    chunk_index: int
    page_number: int | None = None
    metadata: dict = Field(default_factory=dict)