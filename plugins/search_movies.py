
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from translation import *
import urllib.parse
from helpers.get_movie import get_movies
from helpers.send_movies import send_movie_pvt_handler
from helpers.validate_query import validate_q
from helpers.auto_delete import auto_delete

@Client.on_message(filters.private & filters.incoming & ~filters.command(['start', 'total']))
async def find_movies(c: Client, m:Message):
    reply_markup = None
    query = m.text
    query = await validate_q(query)
    if query and m.text:
        reply_markup = await get_movies(query=query, m=m)
        if reply_markup is None or reply_markup is False: 
            await send_movie_pvt_handler(m=m, query=query, reply_markup=reply_markup)

    reply_markup = reply_markup if reply_markup is not None else None
    await auto_delete(m, reply_markup) 

@Client.on_message(filters.private & filters.text)
async def pm_search(client, message):
    btn = [[
            InlineKeyboardButton("Here", url=FILMS_LINK)
        ]]
    await message.reply_text(f'Total results found in this group', reply_markup=InlineKeyboardMarkup(btn))    

    
def escape_url(str):
    return urllib.parse.quote(str)
