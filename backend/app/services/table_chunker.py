from app.schemas.chunk import DocumentChunk
from app.schemas.parsed_document import ParsedDocument
from app.services.chunkers import ChunkingStrategy


class TableChunker(ChunkingStrategy):

    def chunk(
        self,
        document: ParsedDocument
    ) -> list[DocumentChunk]:

        chunks = []
        chunk_index = 0

        for page in document.pages:

            tables = page.metadata.get("tables", [])

            for table in tables:

                rows = table.get("rows", [])

                if not rows:
                    continue

                headers = rows[0]

                for row in rows[1:]:

                    values = []

                    for header, value in zip(headers, row):

                        if header and value is not None:

                            values.append(
                                f"{header}: {value}"
                            )

                    if not values:
                        continue

                    content = "\n".join(values)

                    chunks.append(
                        DocumentChunk(
                            content=content,
                            chunk_index=chunk_index,
                            page_number=page.page_number,
                            metadata={
                                "source": document.source,
                                "file_type": document.file_type,
                                "chunking_strategy": "table_row"
                            }
                        )
                    )

                    chunk_index += 1

        return chunks