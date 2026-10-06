from pydantic import BaseModel, Field


class DocumentPage(BaseModel):

    page_number: int

    content: str

    metadata: dict = Field(
        default_factory=dict
    )


class ParsedDocument(BaseModel):

    source: str

    file_type: str

    page_count: int

    document_type: str = "text"

    pages: list[DocumentPage] = Field(
        default_factory=list
    )

    metadata: dict = Field(
        default_factory=dict
    )

    @property
    def full_text(self) -> str:

        return "\n".join(
            page.content
            for page in self.pages
        )