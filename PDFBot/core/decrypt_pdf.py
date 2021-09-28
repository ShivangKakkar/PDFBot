from PyPDF2.pdf import PdfFileReader, PdfFileWriter
from PyPDF2.utils import PdfReadError


async def decrypt_pdf(path, output, password: str):
    reader = PdfFileReader(path)
    writer = PdfFileWriter()
    reader.decrypt(password)
    try:
        for num in range(reader.numPages):
            writer.addPage(reader.getPage(num))
        with open(output, 'wb') as f:
            writer.write(f)
        return True
    except PdfReadError:
        return False


# decrypt_pdf("encrypted.pdf", "encrypted2.pdf", "dam")
