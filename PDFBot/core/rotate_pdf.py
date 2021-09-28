from PyPDF2.pdf import PdfFileReader, PdfFileWriter


async def rotate_pdf(path, output, direction, numbers=None):
    reader = PdfFileReader(path)
    writer = PdfFileWriter()
    if not numbers:
        numbers = range(reader.numPages)
    else:
        numbers = [number-1 for number in numbers]
    for num in range(reader.numPages):
        if num not in numbers:
            writer.addPage(reader.getPage(num))
            continue
        if direction == 'right':
            page = reader.getPage(num).rotateClockwise(90)
        elif direction == 'left':
            page = reader.getPage(num).rotateCounterClockwise(90)
        else:
            page = reader.getPage(num).rotateClockwise(180)
        writer.addPage(page)
    with open(output, 'wb') as f:
        writer.write(f)
