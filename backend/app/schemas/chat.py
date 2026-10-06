from pydantic import BaseModel


class ChatRequest(BaseModel):

    message: str

    user_id: str

    document_id: int

    conversation_id: str | None = None

    temperature: float = 0.2