from PyPDF2.pdf import PdfFileReader, PdfFileWriter


async def split_pdf(path, output_prefix, numbers: list):
    try:
        reader = PdfFileReader(path)
        files = {}
        start = 0
        numbers.append(reader.numPages+1)
        for number in numbers:
            if number == 1:
                continue
            writer = PdfFileWriter()
            for num in range(start, number-1):
                writer.addPage(reader.getPage(num))
            file = f"{output_prefix}{numbers.index(number)+1}.pdf"
            with open(file, 'wb') as f:
                writer.write(f)
            pages = [i+1 for i in range(start, number-1)]
            files[file] = pages
            start = number-1
        return files
    except IndexError:  # In case the numbers given in numbers list don't exist in the PDF.
        return False
