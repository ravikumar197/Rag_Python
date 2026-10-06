from app.schemas.chunk import DocumentChunk
from app.services.embedding_service import EmbeddingService
from app.services.similarity_service import SimilarityService


class RetrievalService:

    def __init__(
        self,
        embedding_service: EmbeddingService
    ):
        self.embedding_service = embedding_service
        self.similarity_service = SimilarityService()

    def retrieve(
        self,
        query: str,
        chunks: list[DocumentChunk],
        top_k: int = 3
    ):

        query_vector = self.embedding_service.embed_text(query)

        results = []

        for chunk in chunks:

            chunk_vector = self.embedding_service.embed_text(
                chunk.content
            )

            score = self.similarity_service.cosine_similarity(
                query_vector,
                chunk_vector
            )

            results.append({
                "chunk": chunk,
                "score": score
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:top_k]