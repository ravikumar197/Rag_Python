from app.db.database import Base, engine
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.message import Message
from app.models.conversation import Conversation

Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")