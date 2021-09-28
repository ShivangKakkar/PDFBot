from pyrogram import Client, filters
from PDFBot.core import extract_info
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from PyPDF2.pdf import PdfFileReader
import warnings


merging = {}


@Client.on_message(filters.private & filters.document & filters.incoming)
async def main(_, msg: Message):
    user_id = msg.from_user.id
    warnings.filterwarnings("ignore")  # Too much warnings
    if not msg.document.file_name.endswith(".pdf"):
        return
    if user_id in merging and merging[user_id]:
        return
    status = await msg.reply("Downloading PDF...", quote=True)
    pdf = await msg.download(file_name=f"downloads/{msg.from_user.id}/1.pdf")
    pdf_object = PdfFileReader(pdf)
    info = extract_info(pdf)
    buttons = [
        [InlineKeyboardButton("Rotate PDF", callback_data="rotate")],
    ]
    if pdf_object.isEncrypted:
        buttons.append([InlineKeyboardButton("Decrypt PDF", callback_data="decrypt")])
    else:
        buttons.append([InlineKeyboardButton("Encrypt PDF", callback_data="encrypt")])
    buttons.append([InlineKeyboardButton("Merge PDFs", callback_data="merge")])
    await status.delete()
    await msg.reply(
        f"**PDF Information** \n\n{info} \n\nUse below buttons to act on the pdf file.",
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )
