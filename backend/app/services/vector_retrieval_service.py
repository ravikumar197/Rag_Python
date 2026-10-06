
from sqlalchemy.orm import Session

from app.services.embedding_service import EmbeddingService
from app.repositories.document_chunk_repository import search_similar_chunks


class VectorRetrievalService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    def retrieve(
        self,
        db: Session,
        query: str,
        document_id: int,
        top_k: int = 5,
        similarity_threshold: float = 0.60
    ):
        """
        Retrieve the most relevant document chunks.

        The underlying database search uses cosine distance,
        where lower values indicate greater similarity.

        similarity_threshold is therefore interpreted as the
        maximum allowed cosine distance.
        """

        query_embedding = self.embedding_service.embed_text(
            query
        )

        results = search_similar_chunks(
            db=db,
            query_embedding=query_embedding,
            document_id=document_id,
            top_k=top_k,
            distance_threshold=similarity_threshold
        )

        return results