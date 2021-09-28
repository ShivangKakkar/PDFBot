import os
import shutil
from asyncio.exceptions import TimeoutError
from Data import Data
import warnings
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from PDFBot.core import (
    encrypt_pdf,
    decrypt_pdf,
    rotate_pdf,
    merge_pdfs,
    extract_text,
    split_pdf
)
from PDFBot.main import merging


# Callbacks
@Client.on_callback_query()
async def _callbacks(bot: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    directory = f"downloads/{user_id}"
    warnings.filterwarnings("ignore")  # Too much warnings
    try:
        user = await bot.get_me()
        output_prefix = f"{directory}/{user_id}_"
        mention = user["mention"]
        query = callback_query.data.lower()
        if query.startswith("home"):
            if query == 'home':
                chat_id = callback_query.from_user.id
                message_id = callback_query.message.message_id
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=Data.START.format(callback_query.from_user.mention, mention),
                    reply_markup=InlineKeyboardMarkup(Data.buttons),
                )
        elif query == "about":
            chat_id = callback_query.from_user.id
            message_id = callback_query.message.message_id
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=Data.ABOUT,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(Data.home_buttons),
            )
        elif query == "help":
            chat_id = callback_query.from_user.id
            message_id = callback_query.message.message_id
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="**Here's How to use me**\n" + Data.HELP,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(Data.home_buttons),
            )
        elif query == "rotate":
            await callback_query.answer()
            pages_text = "Please tell me which pages to rotate. \n\n**ALL PAGES** \nTo rotate all pages, send 'all' \n\n**SPECIFIC PAGES** \nTo rotate specific pages, separate them by space. \nExample: '1 4 10' or '34 78 93 100'"
            direction_text = "Please tell me how to rotate the pages. \n\n**RIGHT** \nTo rotate the pages to right direction (90 degrees Clockwise), send 'right' \n\n**LEFT** \nTo rotate the pages to left direction (90 degrees Anticlockwise), send 'left' \n\n**UPSIDE** \nTo rotate the pages to upside down (180 degrees), send 'upside'"
            pages = await bot.ask(user_id, pages_text)
            while True:
                if pages.text.lower() == "all":
                    numbers = "all"
                else:
                    numbers = pages.text.split()
                    numbers = [int(page) for page in numbers if page.isdigit()]
                if not numbers:
                    pages = await bot.ask(user_id, "Wrong Format. \n\nPlease send again now.", reply_to_message_id=pages.message_id)
                else:
                    pages = numbers
                    break
            direction = await bot.ask(user_id, direction_text)
            while True:
                if direction.text.lower() in ["left", "right", "upside"]:
                    break
                direction = await bot.ask(user_id, "Direction can only be 'left', 'right' or 'upside'. \n\nSend direction again now.", reply_to_message_id=direction.message_id)
            direction = direction.text.lower()
            output = output_prefix+"rotate.pdf"
            await callback_query.answer("Sending Rotated PDF...")
            pdf = await get_pdf(user_id)
            if pages == "all":
                await rotate_pdf(pdf, output, direction)
            else:
                await rotate_pdf(pdf, output, direction, numbers=pages)
            await callback_query.message.reply_document(output, caption=f"Rotated by @StarkBots")
        elif query == "decrypt":
            await callback_query.answer()
            data = await bot.ask(user_id, "Please provide the original password for decryption.")
            if await cancelled(data):
                return
            pdf = await get_pdf(user_id)
            output = output_prefix+"decrypted.pdf"
            success = await decrypt_pdf(pdf, output, data.text)
            while True:
                if success:
                    break
                else:
                    data = await bot.ask(user_id, "The provided password for decryption is incorrect. Please try again or /cancel", filters=filters.text)
                    if await cancelled(data):
                        return
                    success = await decrypt_pdf(pdf, output, data.text)
            await callback_query.message.reply_document(output, quote=True, caption=f"Decrypted by @StarkBots")
            os.remove(pdf)
            os.remove(output)
        elif query == "encrypt":
            await callback_query.answer()
            data = await bot.ask(user_id, "Please provide a password for encryption.")
            if await cancelled(data):
                return
            pdf = await get_pdf(user_id)
            output = output_prefix+"encrypted.pdf"
            await encrypt_pdf(pdf, output, data.text)
            await callback_query.message.reply_document(output, quote=True, caption=f"Encrypted with password : `{data.text}` \n\nBy @StarkBots")
        elif query == "merge":
            merging[user_id] = True
            await callback_query.answer()
            pdf_msg = await bot.ask(user_id, "Please send more PDFs to merge", filters=filters.document)
            output = output_prefix+"merged.pdf"
            while True:
                if not pdf_msg.document.file_name.endswith(".pdf"):
                    pdf_msg = await pdf_msg.reply("This is not a PDF. Please send a PDF.", quote=True)
                    continue
                status = await pdf_msg.reply("Downloading PDF...", quote=True)
                number = len(os.listdir(f"{directory}")) + 1
                await pdf_msg.download(file_name=f"{directory}/{number}.pdf")
                await status.delete()
                new_pdf_msg = await bot.ask(user_id, f'Send more PDFs or press /merge. \n\nTotal PDFs till now : {len(os.listdir(directory))}. \n\nUse /cancel to cancel.', reply_to_message_id=pdf_msg.message_id)
                if await cancelled(new_pdf_msg):
                    break
                elif new_pdf_msg.text and new_pdf_msg.text.lower() == "/merge":
                    merging[user_id] = False
                    status = await new_pdf_msg.reply("Merging and Uploading...", quote=True)
                    paths = [directory+'/'+file for file in os.listdir(directory)]
                    await merge_pdfs(paths, output)
                    await callback_query.message.reply_document(output, caption=f"Merged {len(paths)} PDFs \n\nBy @StarkBots")
                    await status.delete()
                    break
                elif new_pdf_msg.document:
                    pdf_msg = new_pdf_msg
                else:
                    pdf_msg = await bot.ask(user_id, 'Please send more PDFs or press /merge. \n\nUse /cancel to cancel.')
            merging[user_id] = False
        elif query == "extract":
            await callback_query.answer()
            pages_text = "Please give me the pages numbers from which you want to extract text. Separate multiple numbers by space. \n\nExample: '1 4 10' or '34 78 93 100'"
            pages = await bot.ask(user_id, pages_text)
            while True:
                numbers = pages.text.split()
                numbers = [int(page) for page in numbers if page.isdigit()]
                if not numbers:
                    pages = await bot.ask(user_id, "Wrong Format. \n\nPlease send again now.", reply_to_message_id=pages.message_id)
                else:
                    break
            if await cancelled(pages):
                return
            pdf = await get_pdf(user_id)
            for number in numbers:
                text = await extract_text(pdf, number)
                if len(text) >= 4096:
                    texts = [text[i:i+4096] for i in range(0, len(text), 4096)]
                    for text in texts:
                        await callback_query.message.reply(text)
                else:
                    await callback_query.message.reply(text)
        elif query == "split":
            await callback_query.answer()
            pages_text = "Please give me the pages which will be used to split pdf. Separate multiple numbers by space. \n\nEvery number you give will be first page of a new pdf. \n\nExample if you gave '4 10 19' then I'll split the PDF into 4 PDFs. First PDF with pages 1-3, second with 4-9, third with 10-18 and 4th with 19 till end."
            pages = await bot.ask(user_id, pages_text)
            while True:
                numbers = pages.text.split()
                numbers = [int(page) for page in numbers if page.isdigit()]
                if not numbers:
                    pages = await bot.ask(user_id, "Wrong Format. \n\nPlease send again now.", reply_to_message_id=pages.message_id)
                else:
                    break
            if await cancelled(pages):
                return
            pdf = await get_pdf(user_id)
            output_prefix = f"{directory}/Split File "
            files = await split_pdf(pdf, output_prefix, numbers)
            if not files:
                await callback_query.message.reply("A provided page number doesn't exist. Cancelling.")
                shutil.rmtree(directory, ignore_errors=True)
                return
            for file in files:
                pages = files[file]
                if len(pages) == 0:
                    await callback_query.message.reply("A provided page number doesn't exist. Cancelling.")
                else:
                    to = f"{pages[0]} to {pages[-1]}" if not len(pages) == 1 else pages[0]
                    caption = f"Split File {list(files.keys()).index(file)+1} \n\nPages {to} \nTotal Pages : {len(pages)} \n\nBy @StarkBots"
                    await callback_query.message.reply_document(file, caption=caption)
    except TimeoutError:
        merging[user_id] = False
        pass
    except FileNotFoundError:
        await callback_query.message.reply("Please send me the file again as it doesn't exist now.")
        await callback_query.message.delete()
    shutil.rmtree(directory, ignore_errors=True)


async def cancelled(msg):
    if msg.text and msg.text.startswith("/cancel"):
        await msg.reply("Cancelled the Process.", quote=True)
        return True
    else:
        return False


async def get_pdf(user_id):
    files = os.listdir(f"downloads/{user_id}")
    answer = []
    for file in files:
        if file.startswith(str(user_id)):
            pass
        elif file.endswith(".pdf"):
            answer.append(file)
        else:
            os.remove(file)
    if len(answer) == 0:
        # In case forwarded a file starting with name "user_id"
        if len(files) == 1:
            return f"downloads/{user_id}/{files[0]}"
        else:
            return files
    elif len(answer) == 1:
        return f"downloads/{user_id}/{answer[0]}"
    else:
        return answer
