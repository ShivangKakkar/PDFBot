from PyPDF2.pdf import PdfFileReader, PdfFileWriter


async def encrypt_pdf(path, output, password: str):
    reader = PdfFileReader(path)
    writer = PdfFileWriter()
    for num in range(reader.numPages):
        writer.addPage(reader.getPage(num))
    writer.encrypt(user_pwd=password)
    with open(output, 'wb') as f:
        writer.write(f)


# encrypt_pdf("encrypted.pdf", "encrypted2.pdf", "hotdamn")
