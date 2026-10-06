from abc import ABC, abstractmethod

from app.schemas.parsed_document import ParsedDocument


class DocumentProcessor(ABC):

    @abstractmethod
    def extract(
        self,
        file_path: str,
        source: str,
        file_type: str
    ) -> ParsedDocument:
        pass