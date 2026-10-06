from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str
    file_type: str
    file_size: int


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    status: str