
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from .database import add_file
from config import ADMINS, DEFAULT_PHOTO
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Add Movie to database
@Client.on_message(filters.user(ADMINS) & filters.private & filters.media)
async def web_db(c: Client, m: Message):
    # if m.text:
    #     if m.text.startswith("/"):
    #         await m.continue_propagation()
    #         return

    #     if len(m.text) < 2:
    #         await m.continue_propagation()
    #         return
    
    if (m.caption and m.photo) or m.text:
        message = m.caption or m.text
        if not m.photo:
            file_id = DEFAULT_PHOTO
            file_unique_id = random.randint(1000, 9999)
        else:
            file_id = m.photo.file_id
            file_unique_id = m.photo.file_unique_id
        
        res = {
            "caption": message.html,
            "title": message.splitlines()[0],
            "thumbnail": file_id,
            "unique_id": file_unique_id,
        }
        _id = await add_file(**res)

        if not _id:
            await m.reply("This file already exists")
            return

        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Delete", callback_data=f"delete#{_id.inserted_id }"
                    )
                ],
            ]
        )

        await m.reply("Added Successfully", reply_markup=reply_markup)

    else:
        await m.reply("Something went wrong")
