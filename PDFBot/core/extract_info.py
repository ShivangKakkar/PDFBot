from PyPDF2.pdf import PdfFileReader
from PyPDF2.utils import PdfReadError


def extract_info(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        try:
            number_of_pages = pdf.getNumPages()
        except PdfReadError:
            return "This is an Encrypted File. \n\nYou can't act on it until it's decrypted. \n\nDecrypt it first and then send the decrypted file back!"
        information = pdf.getDocumentInfo()
    info = ''
    if information.title:
        info += f"**Title:** {information.title}"
    info += f"\n**Number of pages:** {number_of_pages}"
    info += f"\n**Encrypted:** {pdf.isEncrypted}"
    if information.producer:
        info += f"\n**Producer:** {information.producer}"
    if information.author:
        info += f"\n**Author:** {information.author}"
    if information.creator:
        info += f"\n**Creator:** {information.creator}"
    if information.subject:
        info += f"\n**Subject:** {information.subject}"
    return info
