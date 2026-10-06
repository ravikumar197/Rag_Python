from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.schemas.chunk import DocumentChunk as DocumentChunkSchema
from app.services.embedding_service import EmbeddingService


class EmbeddingStorageService:

    def __init__(
        self,
        embedding_service: EmbeddingService
    ):
        self.embedding_service = embedding_service

    def store_chunks(
        self,
        db: Session,
        document_id: int,
        chunks: list[DocumentChunkSchema]
    ):

        try:

            texts = [
                chunk.content
                for chunk in chunks
            ]

            embeddings = self.embedding_service.embed_documents(
                texts
            )

            db_chunks = []

            for chunk, embedding in zip(chunks, embeddings):

                db_chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    embedding=embedding
                )

                db.add(db_chunk)
                db_chunks.append(db_chunk)

            db.commit()

            for db_chunk in db_chunks:
                db.refresh(db_chunk)

            return db_chunks

        except Exception:
            db.rollback()
            raise