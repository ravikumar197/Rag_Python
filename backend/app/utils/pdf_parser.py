import pymupdf

def extract_text_from_pdf(file_path: str) -> str:

    document = pymupdf.open(file_path)

    pages = []

    for page in document:
        text = page.get_text()

        if text.strip():
            pages.append(text)

    document.close()

    return "\n".join(pages)