from sqlalchemy.orm import Session
from app.models.document import Document
from app.processors.factory import DocumentProcessorFactory
# from app.services.fixed_chunker import FixedSizeChunker
# from app.services.structure_chunker import StructureAwareChunker

from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.embedding_storage_service import EmbeddingStorageService


class DocumentIngestionService:

    def __init__(self):

        self.embedding_service = EmbeddingService()

        self.embedding_storage_service = EmbeddingStorageService(
            self.embedding_service
        )

        self.chunking_service = ChunkingService()

    def ingest(
        self,
        db: Session,
        document_id: int,
        file_path: str,
        filename: str,
        file_type: str
    ):

        document_record = db.get(
            Document,
            document_id
        )

        if document_record is None:
            raise ValueError(
                f"Document {document_id} not found"
            )

        try:

            # Processing started
            document_record.status = "processing"
            db.commit()

            # Processor
            processor = DocumentProcessorFactory.get_processor(
                file_type
            )

            # Extract
            document = processor.extract(
                file_path,
                filename,
                file_type
            )

            # Chunk
            chunks = self.chunking_service.chunk(
                document
            )

            # Embed + store
            stored_chunks = self.embedding_storage_service.store_chunks(
                db=db,
                document_id=document_id,
                chunks=chunks
            )

            # Processing completed
            document_record.status = "completed"

            db.commit()
            db.refresh(document_record)

            return {
                "document": document_record,
                "chunks": stored_chunks
            }

        except Exception:

            document_record.status = "failed"

            db.commit()

            raise