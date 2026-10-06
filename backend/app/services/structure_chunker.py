import re

from app.schemas.chunk import DocumentChunk
from app.schemas.parsed_document import ParsedDocument
from app.services.chunkers import ChunkingStrategy


class StructureAwareChunker(ChunkingStrategy):

    def __init__(
        self,
        record_pattern: str
    ):
        self.record_pattern = re.compile(record_pattern)

    def chunk(
        self,
        document: ParsedDocument
    ) -> list[DocumentChunk]:

        chunks = []
        chunk_index = 0

        for page in document.pages:

            lines = [
                line.strip()
                for line in page.content.splitlines()
                if line.strip()
            ]

            current_record = []

            for line in lines:

                if self.record_pattern.match(line):

                    if current_record:

                        chunks.append(
                            DocumentChunk(
                                content="\n".join(current_record),
                                chunk_index=chunk_index,
                                page_number=page.page_number,
                                metadata={
                                    "source": document.source,
                                    "file_type": document.file_type,
                                    "chunking_strategy": "structure_aware"
                                }
                            )
                        )

                        chunk_index += 1

                    current_record = [line]

                else:

                    current_record.append(line)

            if current_record:

                chunks.append(
                    DocumentChunk(
                        content="\n".join(current_record),
                        chunk_index=chunk_index,
                        page_number=page.page_number,
                        metadata={
                            "source": document.source,
                            "file_type": document.file_type,
                            "chunking_strategy": "structure_aware"
                        }
                    )
                )

                chunk_index += 1

        return chunks