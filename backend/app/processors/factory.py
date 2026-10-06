from fastapi import HTTPException

from app.processors.pdf_processor import PDFProcessor


class DocumentProcessorFactory:

    @staticmethod
    def get_processor(file_type: str):

        if file_type == "application/pdf":
            return PDFProcessor()

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_type}"
        )