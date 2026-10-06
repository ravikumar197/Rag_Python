from pydantic import BaseModel


class SearchRequest(BaseModel):

    query: str

    document_id: int

    top_k: int = 5