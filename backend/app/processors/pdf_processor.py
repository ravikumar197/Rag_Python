import pymupdf

from app.processors.base import DocumentProcessor
from app.schemas.parsed_document import (
    DocumentPage,
    ParsedDocument
)


class PDFProcessor(DocumentProcessor):

    def extract(
        self,
        file_path: str,
        source: str,
        file_type: str
    ) -> ParsedDocument:

        document = pymupdf.open(file_path)

        pages = []

        has_table = False
        has_text = False

        for page_number, page in enumerate(document):

            text = page.get_text().strip()

            if text:
                has_text = True

            # Detect tables generically
            tables = page.find_tables()

            page_tables = []

            if tables.tables:

                has_table = True

                for table in tables.tables:

                    rows = table.extract()

                    page_tables.append({
                        "rows": rows
                    })

            pages.append(
                DocumentPage(
                    page_number=page_number + 1,
                    content=text,
                    metadata={
                        "has_table": bool(tables.tables),
                        "tables": page_tables
                    }
                )
            )

        page_count = len(pages)

        document.close()

        if has_table and has_text:
            document_type = "mixed"

        elif has_table:
            document_type = "table"

        else:
            document_type = "text"

        return ParsedDocument(
            source=source,
            file_type=file_type,
            page_count=page_count,
            document_type=document_type,
            pages=pages,
            metadata={
                "has_tables": has_table
            }
        )