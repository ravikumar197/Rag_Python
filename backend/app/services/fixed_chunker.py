from app.schemas.chunk import DocumentChunk
from app.schemas.parsed_document import ParsedDocument
from app.services.chunkers import ChunkingStrategy


class FixedSizeChunker(ChunkingStrategy):

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(
        self,
        document: ParsedDocument
    ) -> list[DocumentChunk]:

        chunks = []
        chunk_index = 0

        for page in document.pages:

            text = page.content.strip()

            if not text:
                continue

            start = 0

            while start < len(text):

                end = start + self.chunk_size

                chunk_text = text[start:end]

                chunks.append(
                    DocumentChunk(
                        content=chunk_text,
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        metadata={
                            "source": document.source,
                            "file_type": document.file_type,
                            "chunking_strategy": "fixed_size"
                        }
                    )
                )

                chunk_index += 1

                start = end - self.chunk_overlap

        return chunks