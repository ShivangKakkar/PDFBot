from PyPDF2.pdf import PdfFileReader


async def extract_text(path: str, page: int):
    page = page - 1
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        try:
            page_object = pdf.getPage(page)
            text = page_object.extractText()
        except IndexError:
            text = f"Page number {page + 1} doesn't exist."
    return text
