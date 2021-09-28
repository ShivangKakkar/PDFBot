from PyPDF2.pdf import PdfFileReader, PdfFileWriter


async def merge_pdfs(paths, output):
    writer = PdfFileWriter()
    for path in paths:
        reader = PdfFileReader(path)
        for num in range(reader.numPages):
            writer.addPage(reader.getPage(num))
    with open(output, 'wb') as f:
        writer.write(f)


# merge_pdfs(["sample.pdf", "sample2.pdf"], "merged_1.pdf")
