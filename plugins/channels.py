
from pyrogram import Client, filters
from pyrogram.types import Message
from .database import add_file
from config import *
from pyrogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)



@Client.on_message(filters.chat(CHANNELS_LIST) & filters.media & filters.channel & filters.incoming)
async def channel_movie_handler(c: Client, m: Message):
    if CHANNELS == "True":
        if m.caption and m.photo:
            message = m.caption

            res = {
                "caption": message.html,
                "title": message.splitlines()[0],
                "thumbnail": m.photo.file_id,
                "unique_id": m.photo.file_unique_id,
            }
            _id = await add_file(**res)

            if not _id:
                return

            reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Delete", callback_data=f"delete#{_id.inserted_id}")],
            ])
            await c.send_message(
                chat_id=OWNER_ID,
                text=f"Post Added Successfully\n\nPost Link: [Click]({m.link})\n\nTittle: <code>{message.splitlines()[0]}</code>",
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        else:
            await c.send_message(
                chat_id=OWNER_ID,
                text=f"Something went wrong on adding post \n\nPost Link: [Click]({m.id})\n\nTittle: <code>{message.splitlines()[0]}</code>",
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
