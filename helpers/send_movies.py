import asyncio
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from translation import *
import urllib.parse
from helpers.spell_check import advantage_spell_chok

from helpers.auto_delete import auto_delete

BUTTONS = {}

async def send_movie_pvt_handler(m: Message, query:str, reply_markup):
    if reply_markup is False: # query is empty
        return 

    elif reply_markup is None: # if we don't find a movie in database
        if USE_OMDB:
            is_movie_found, reply_markup = await advantage_spell_chok(m, query)
            if is_movie_found:
                txt = await m.reply(text="I couldn't find anything related to that\nDid you mean any one of these?", reply_markup=reply_markup)
                await auto_delete(m, txt)
                return 

        google_search_url = "https://www.google.com/search?q=" + await escape_url(f"{m.text} Movie")
        release_date_url = "https://www.google.com/search?q=" + await escape_url(f"{m.text} Release Date")

        reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Check correct spelling ✅", url=google_search_url)],
            [InlineKeyboardButton("Check realease date 📅", url=release_date_url)]
        ])

        txt = await m.reply(text=NO_RESULTS_FOUND.format(m.text, "https://www.google.com/search"), reply_markup=reply_markup)
      #  if NO_RESULTS_MSG:
      #              await bot.send_message(chat_id=LOG_CHANNEL, text=f"THIS NOT FOUND SIR <code>{query}<code>")
        await auto_delete(m, txt)

# Group handlers for search results
async def send_movie_group_handler(m: Message, query:str, reply_markup):

    if reply_markup is False: # query is empty
        return 

    elif reply_markup is None: # if we don't find a movie in database
        if USE_OMDB:
            is_movie_found, reply_markup = await advantage_spell_chok(m, query)
            if is_movie_found:
                txt = await m.reply(text="I couldn't find anything related to that\nDid you mean any one of these?", reply_markup=reply_markup)
                await auto_delete(m, txt)
                return 

        # if movie is not available in google also

        google_search_url = "https://www.google.com/search?q=" + await escape_url(f"{m.text} Movie")
        release_date_url = "https://www.google.com/search?q=" + await escape_url(f"{m.text} Release Date")

        reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Check correct spelling ✅", url=google_search_url)],
            [InlineKeyboardButton("Check realease date 📅", url=release_date_url)]
        ])

        txt = await m.reply(text=NO_RESULTS_FOUND.format(m.text, "https://www.google.com/search"), reply_markup=reply_markup)
        await auto_delete(m, txt)

async def escape_url(str):
    return urllib.parse.quote(str)


