import os
import random
import sys
import asyncio
import contextlib
from config import *
from translation import BATCH
from plugins.database import add_file

from config import ADMINS
from pyrogram import Client, filters
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


cancel_button = [[InlineKeyboardButton(
    "Cancel 🔐", callback_data="cancel_process")]]


@Client.on_message(filters.private & filters.command("batch") & filters.chat(ADMINS))
async def batch(c, m):
    if len(m.command) < 2:
        await m.reply_text(BATCH)
    else:
        channel_id = m.command[1]
        if channel_id.startswith("@"):
            channel_id = channel_id.split("@")[1]
        elif channel_id.startswith("-100"):
            channel_id = int(channel_id)
        elif channel_id.startswith("t.me"):
            channel_id = channel_id.split("/")[-1]
            if channel_id.startswith(
                ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")
            ):
                channel_id = int(channel_id)
            else:
                channel_id = str(channel_id)
        elif channel_id.startswith("https"):
            channel_id = channel_id.split("/")[-1]

        buttons = [
            [
                InlineKeyboardButton(
                    "Batch Short 🏕", callback_data=f"batch_{channel_id}"
                )
            ],
            [InlineKeyboardButton("Cancel 🔐", callback_data="cancel")],
        ]

        return await m.reply(
            text=f"Are you sure you want to batch short?\n\nChannel: {channel_id}",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


@Client.on_callback_query(filters.regex(r"^cancel") | filters.regex(r"^batch"))
async def cancel(c: Client, m):
    if m.data == "cancel":
        await m.message.delete()
        return
    elif m.data.startswith("batch"):
        info_text = "Batch Shortening Started!\n\n Channel: {}\n\nTo Cancel /cancel\n\n Message Saved: {}"
        channel_id = m.data.split("_")[1]

        count = 0
        try:
            txt = await c.send_message(int(channel_id), ".")
            await txt.delete()

        except ChatWriteForbidden:
            await m.message.edit("Bot is not an admin in the given channel")
        await m.message.edit(text=info_text.format(channel_id, 0))

        total_messages = range(1, txt.id)
        for i in range(0, len(total_messages), 200):
            channel_posts = await c.get_messages(channel_id, total_messages[i: i + 200])

            for post in channel_posts:
                try:
                    phot_post = post.caption and post.photo
                    if phot_post or post.text:
                        message = post.caption or post.text
                        if post.photo:
                            file_id = post.photo.file_id
                            file_unique_id = post.photo.file_unique_id
                        else:
                            file_id = DEFAULT_PHOTO
                            file_unique_id = random.randint(1000, 6666666)
                        res = {
                            "caption": message.html,
                            "title": message.splitlines()[0],
                            "thumbnail": file_id,
                            "unique_id": file_unique_id,
                        }
                        await add_file(**res)
                        count += 1
                        if count % 20 == 0:
                            with contextlib.suppress(Exception):
                                await m.message.edit(text=info_text.format(channel_id, count))

                except Exception as e:
                    print(e)
                    await c.send_message(chat_id=OWNER_ID, text=e)

        return await m.message.edit(
            text=f"Message Saved: {count}" + "\n\nBatch Completed"
        )


@Client.on_message(filters.command("cancel"))
async def stop_button(c, m):
    if m.from_user.id in ADMINS:
        print("Cancelled")
        msg = await c.send_message(
            text="<i>Trying To Stoping.....</i>", chat_id=m.chat.id
        )
        await asyncio.sleep(5)
        await msg.edit("Batch Shortening Stopped Successfully 👍")
        os.execl(sys.executable, sys.executable, *sys.argv)

