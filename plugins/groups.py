import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.forcesub import forcesub_handler
from .database import collection
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from translation import *
from plugins.callback import replace_username
from bson.objectid import ObjectId
from plugins.search_movies import escape_url
from helpers.validate_query import validate_q
from helpers.send_movies import send_movie_group_handler
from helpers.get_movie import get_movies
from helpers.auto_delete import auto_delete

@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_handler(c: Client, m:Message):
    if FORCESUB == 'True' and not await forcesub_handler(c, m):
        return
    reply_markup = None
    query = m.text
    query = await validate_q(query)
    if query and m.text:
        reply_markup = await get_movies(query=query, m=m)
        if reply_markup is None or reply_markup is False:
            await send_movie_group_handler(m=m, query=query, reply_markup=reply_markup)

    reply_markup = reply_markup if reply_markup is not None else None

    await auto_delete(m, reply_markup)
    return
    

async def group_send_handler(c: Client, m:Message):
    if FORCESUB == 'True' and not await forcesub_handler(c, m):
        return
    txt = await m.reply('Processing...')
    id  = m.command[1]
    result = await collection.find_one({'_id': ObjectId(id)})
    caption = result['caption']
    caption = await replace_username(caption)

    if m.chat.id in ADMINS:  
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Delete", callback_data=f"delete#{id}")],
            ])
    else:
        reply_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Join", url=f"https://t.me/{USERNAME}")],
        ])   

    await txt.edit(
        f"**{caption}**", 
        disable_web_page_preview=True, 
        reply_markup=reply_markup)