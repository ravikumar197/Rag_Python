from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


def search_similar_chunks(
    db: Session,
    query_embedding: list[float],
    document_id: int,
    top_k: int = 5,
    distance_threshold: float | None = None
):
    """
    Search for the most similar document chunks using cosine distance.

    Lower cosine distance means higher similarity.

    Args:
        db: SQLAlchemy database session.
        query_embedding: Embedding vector for the user query.
        document_id: Document to search within.
        top_k: Maximum number of results to return.
        distance_threshold:
            Optional maximum cosine distance allowed.
            Results with a distance greater than this value
            are excluded.
    """

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    conditions = [
        DocumentChunk.document_id == document_id
    ]

    if distance_threshold is not None:
        conditions.append(
            distance <= distance_threshold
        )

    statement = (
        select(
            DocumentChunk,
            distance.label("distance")
        )
        .where(*conditions)
        .order_by(distance)
        .limit(top_k)
    )

    return db.execute(statement).all()
