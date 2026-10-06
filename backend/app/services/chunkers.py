from abc import ABC, abstractmethod

from app.schemas.chunk import DocumentChunk
from app.schemas.parsed_document import ParsedDocument


class ChunkingStrategy(ABC):

    @abstractmethod
    def chunk(
        self,
        document: ParsedDocument
    ) -> list[DocumentChunk]:
        pass