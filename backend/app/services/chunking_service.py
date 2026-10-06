from app.schemas.chunk import DocumentChunk
from app.schemas.parsed_document import ParsedDocument

from app.services.chunkers import ChunkingStrategy
from app.services.fixed_chunker import FixedSizeChunker
from app.services.table_chunker import TableChunker


class ChunkingService:

    def __init__(
        self,
        strategy: ChunkingStrategy | None = None
    ):
        self.strategy = strategy

    def chunk(
        self,
        document: ParsedDocument
    ) -> list[DocumentChunk]:

        if self.strategy:
            return self.strategy.chunk(document)

        if document.document_type == "table":

            return TableChunker().chunk(document)

        if document.document_type == "mixed":

            return self._chunk_mixed(document)

        return FixedSizeChunker(
            chunk_size=500,
            chunk_overlap=100
        ).chunk(document)

    def _chunk_mixed(
        self,
        document: ParsedDocument
    ) -> list[DocumentChunk]:

        chunks = []

        table_chunks = TableChunker().chunk(document)

        chunks.extend(table_chunks)

        return chunks