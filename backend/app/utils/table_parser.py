import pymupdf


def extract_tables_from_pdf(file_path: str):

    document = pymupdf.open(file_path)

    all_tables = []

    for page_number, page in enumerate(document):

        tables = page.find_tables()

        for table in tables.tables:

            rows = table.extract()

            if not rows:
                continue

            headers = rows[0]

            data_rows = rows[1:]

            all_tables.append({
                "page": page_number + 1,
                "headers": headers,
                "rows": data_rows
            })

    document.close()

    return all_tables