from pyrogram.types import Message
from plugins.database import collection
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from translation import *
from helpers.validate_query import validate_q
from helpers.spell_check import search_movie
from helpers.link_to_hyper import link_to_hyperlink
import math

BUTTONS = {}

async def get_movies(query: str, m: Message, offset=0):
    results = await search_for_videos(query)
    if results is not None:
        offset = offset * 10
        list2 = []
        for result in results[offset : offset + RESULTS_COUNT]:
            _id = str(result["_id"])
            
            if m.chat.id in ADMINS:
                list2 += (
                    [
                        InlineKeyboardButton(
                            result["title"], callback_data=f"send#{_id}#{m.chat.id}"
                        ),
                        InlineKeyboardButton("Delete", callback_data=f"delete#{_id}"),
                    ],
                )
            else:
                list2 += (
                    [
                        InlineKeyboardButton(
                            result["title"], callback_data=f"send#{_id}#{m.chat.id}"
                        ),
                    ],
                )

            if len(list2) >= RESULTS_COUNT:
                break

        if int((offset / 10) + 1) < math.ceil(len(results) / 10):

            list2.append(
                [InlineKeyboardButton(text="NEXT ⏩", callback_data=f"next_1_{m.text}")],
            )

        list2.append(
            [
                InlineKeyboardButton(
                    text=f"📃 Pages {int((offset/10)+1)} / {math.ceil(len(results) / 10)}",
                    callback_data="pages",
                )
            ],
        )

        poster= RESULTS_IMAGE

        if USE_OMDB:
            try:
                _, _, _, poster = await search_movie(query)
            except Exception:
                poster= RESULTS_IMAGE

        reply_markup = InlineKeyboardMarkup(list2)
        return (
            await m.reply_text(
                text=f"<b>Hᴇʏ {m.from_user.mention}, Hᴇʀᴇ ɪs Wʜᴀᴛ I Fᴏᴜɴᴅ Iɴ Mʏ Dᴀᴛᴀʙᴀsᴇ Fᴏʀ Yᴏᴜʀ Qᴜᴇʀʏ {query}.</b>",
                reply_markup=reply_markup,
                quote=True,
            )
            if poster
            else await m.reply(
                text=f"Results for {query.title()}",
                reply_markup=reply_markup,
                quote=True,
            )
        )


async def search_for_videos(search_text: str):
    query = await validate_q(search_text)
    x = f'"{query}"'
    pipeline = {"$text": {"$search": x}}
    db_list = collection.find(pipeline, {"score": {"$meta": "textScore"}})

    query = db_list.sort([("score", {"$meta": "textScore"})])
    if quer := [i async for i in query]:
        return quer

class AsyncIter:
    def __init__(self, items):
        self.items = items

    async def __aiter__(self):
        for item in self.items:
            yield item

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration as e:
            raise StopAsyncIteration from e


async def convert_to_hyperlink(query):
    lis = []
    async for i in query:
        cap = await link_to_hyperlink(i["caption"])
        i["caption"] = cap
        lis.append(i)
    return lis


def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]
