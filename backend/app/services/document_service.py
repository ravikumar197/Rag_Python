from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate
from app.repositories import document_repository


def create_document(
    db: Session,
    document_data: DocumentCreate
):

    document = Document(
        filename=document_data.filename,
        file_type=document_data.file_type,
        file_size=document_data.file_size,
        status="uploaded"
    )

    return document_repository.create_document(
        db,
        document
    )


def get_document(
    db: Session,
    document_id: int
):

    return document_repository.get_document(
        db,
        document_id
    )