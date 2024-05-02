import asyncio
import contextlib
from datetime import datetime
import re
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant
from utils import get_group_admins, get_group_info_text
from .database import collection, group_db
from bson.objectid import ObjectId
from config import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helpers.get_movie import get_movies, search_for_videos
from helpers.auto_delete import auto_delete
from helpers.shortener import mdisk_droplink_convertor
import math


@Client.on_callback_query(filters.regex("sub_refresh"))
async def refresh_cb(c, m):
    owner = c.owner
    _, file_id, group_id = m.data.split("#")
    group_config = await group_db.find_chat_without_adding(int(group_id))
    UPDATE_CHANNEL = group_config['fsub_channel']

    try:
        user = await c.get_chat_member(UPDATE_CHANNEL, m.from_user.id)
        if user.status == "kicked":
            with contextlib.suppress(Exception):
                await m.message.edit("**Hey you are banned**")
            return
    except UserNotParticipant:
        await m.answer(
            "You have not yet joined our channel. First join and then press refresh button",
            show_alert=True,
        )

        return
    except Exception as e:
        print(e)
        await m.message.edit(
            f"Something Wrong. Please try again later or contact {owner.mention(style='md')}"
        )
        return

    if file_id and group_id:
        result = await collection.find_one({"_id": ObjectId(file_id)})

        try:
            caption = result["caption"]
        except Exception as e:
            return await m.reply("Some error occurred")

        caption = await replace_username(caption)

        reply_markup = (
            InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Delete", callback_data=f"delete#{id}"
                        )
                    ],
                ]
            )
            if m.message.chat.id in ADMINS
            else InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Join", url=f"https://t.me/{USERNAME}"
                        )
                    ],
                ]
            )
        )

        if IS_SHORTENER_ENABLED:
            shortener_domain = SHORTENER_WEBSITE
            if group_config is not None and group_config.get('shortener_api'):
                shortener_api = group_config['shortener_api']
            else:
                shortener_api = SHORTENER_API
        else:
            shortener_domain = None
            shortener_api = None

        caption = await mdisk_droplink_convertor(caption, shortener_domain, shortener_api)
        caption = CUSTOM_CAPTION.format(caption=caption)
        text = await m.message.reply_photo(
                caption=caption, photo=result["thumbnail"], reply_markup=reply_markup
            )
        await auto_delete(text)

    await m.message.delete()



@Client.on_callback_query(filters.regex('^validity'))
async def change_validity_cb(c, m: CallbackQuery):
    _, group_id, time_in_s = m.data.split("#")
    group_id = int(group_id)
    await group_db.update_group_info(group_id, {"has_access":True, "access_days":int(time_in_s), "last_verified":datetime.now()})
    text = await get_group_info_text(c, group_id)
    await m.edit_message_text(text, reply_markup=m.message.reply_markup)
    await m.answer("Updated Successfully", show_alert=True)

    bin_text = "Your group has been updated\n\n"
    text = bin_text+text
    
    admins = await get_group_admins(c, group_id)
    for user_id in admins:
        await c.send_message(user_id, text)


@Client.on_callback_query(filters.regex('^removeaccess'))
async def removeaccess_cb(c, m: CallbackQuery):
    _, group_id = m.data.split("#")
    group_id = int(group_id)
    await group_db.update_group_info(group_id=group_id, value={"has_access": False,"last_verified":datetime(1970,1,1), "access_days":0})
    text = await get_group_info_text(c, group_id)
    await m.edit_message_text(text, reply_markup=m.message.reply_markup)
    await m.answer("Access has been removed", show_alert=True)


    bin_text = "Your group has been updated\n\n"
    text = bin_text+text
    
    admins = await get_group_admins(c, group_id)
    for user_id in admins:
        await c.send_message(user_id, text)
        
@Client.on_callback_query(filters.regex(r"^send"))
async def cb_send_handler(c, m):
    _, id, group_id = m.data.split("#")

    group_id = int(group_id)

    if m.message.chat.type == enums.ChatType.PRIVATE:
        result = await collection.find_one({"_id": ObjectId(id)})

        try:
            caption = result["caption"]
        except Exception as e:
            return await m.message.reply("Some error occurred")

        caption = await replace_username(caption)

        if m.message.chat.id in ADMINS:
            reply_markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Delete", callback_data=f"delete#{id}")],
                ]
            )
        else:
            reply_markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("How To Download ❓", url=f"https://t.me/{HOWTO}")],
                ]
            )

        if IS_SHORTENER_ENABLED:
            shortener_api = SHORTENER_API
            shortener_domain = SHORTENER_WEBSITE
        else:
            shortener_api = None
            shortener_domain = None

        caption = await mdisk_droplink_convertor(caption, shortener_domain, shortener_api)

        caption = CUSTOM_CAPTION.format(caption=caption)
        text = await m.message.reply_photo(
                caption=caption, photo=result["thumbnail"], reply_markup=reply_markup
            )
        await auto_delete(text)

    elif m.message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        try:
            await m.answer(url=f'https://telegram.me/{c.raw_username}?start=send_{id}_{m.message.chat.id}')
        except Exception as e:
            print(e)
            await m.answer("Some error occured", show_alert=True)
    

@Client.on_callback_query(filters.regex(r"^delete"))
async def cb_delete_handler(c, m):
    try:
        _id = m.data.split("#")[1]
        my_query = {"_id": ObjectId(_id)}
        await collection.delete_one(my_query)
        txt = await m.message.edit("Deleted Successfully")
    except Exception as e:
        print(e)
        txt = await m.message.edit("Some error occurred while deleting")
    await auto_delete(m.message, txt)


async def replace_username(text):

    if not USERNAME:
        return text
    
    usernames = re.findall("([@#][A-Za-z0-9_]+)", text)

    for i in usernames:
        text = text.replace(i, f"@{USERNAME}")

    telegram_links = re.findall(
        r"[(?:http|https)?://]*(?:t.me|telegram.me)[^\s]+", text
    )

    for i in telegram_links:
        text = text.replace(i, f"@{USERNAME}")

    return text


@Client.on_callback_query(filters.regex(r"^close"))
async def cb_close_handler(c, m):
    await m.answer()
    await m.message.delete()


@Client.on_callback_query(filters.regex(r"^spolling"))
async def send_spell_checker(bot, query):
    print(query.data)
    _, user, movie_ = query.data.split("#")
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("Search for yourself", show_alert=True)

    results = await get_movies(movie_, query.message)
    if results is None:
        await query.answer("Movie not found in database", show_alert=True)

    await auto_delete(query.message, results)


# Next Button


@Client.on_callback_query(filters.regex(r"^next"))
async def next_btn_cb_handler(client: Client, query: CallbackQuery):
    txt = None
    print(query.data)
    ident, offset, keyword = query.data.split("_")

    offset = int(offset) * 10
    results = await search_for_videos(keyword)
    if results is not None:
        list2 = []
        for result in results[offset : offset + RESULTS_COUNT]:
            id = str(result["_id"])

            if query.message.chat.id in ADMINS:
                list2 += (
                    [
                        InlineKeyboardButton(
                            result["title"], callback_data=f"send#{id}#{query.message.chat.id}"
                        ),
                        InlineKeyboardButton("Delete", callback_data=f"delete#{id}"),
                    ],
                )
            else:
                list2 += (
                    [
                        InlineKeyboardButton(
                            result["title"], callback_data=f"send#{id}#{query.message.chat.id}"
                        ),
                    ],
                )

            if len(list2) >= RESULTS_COUNT:
                break

        list2.append(
            [
                InlineKeyboardButton(
                    text="BACK", callback_data=f"back_{int(offset/10)-1}_{keyword}"
                )
            ],
        )

        if int((offset / 10) + 1) < math.ceil(len(results) / 10):

            list2.append(
                [
                    InlineKeyboardButton(
                        text="NEXT ⏩",
                        callback_data=f"next_{int(offset/10)+1}_{keyword}",
                    )
                ],
            )

        list2.append(
            [
                InlineKeyboardButton(
                    text=f"📃 Pages {int((offset/10)+1)} / {math.ceil(len(results) / 10)}",
                    callback_data="pages",
                )
            ],
        )

        reply_markup = InlineKeyboardMarkup(list2)
        txt = await query.edit_message_caption(
            caption=f"Results for {keyword}", reply_markup=reply_markup
        )


# Back Button
@Client.on_callback_query(filters.regex(r"^back"))
async def back_btn_cb_handler(client: Client, query: CallbackQuery):

    _, offset, keyword = query.data.split("_")

    offset = int(offset) * 10
    results = await search_for_videos(keyword)
    if results is not None:
        list2 = []
        for result in results[offset : offset + RESULTS_COUNT]:
            id = str(result["_id"])

            if query.message.chat.id in ADMINS:
                list2 += (
                    [
                        InlineKeyboardButton(
                            result["title"], callback_data=f"send#{id}#{query.message.chat.id}"
                        ),
                        InlineKeyboardButton("Delete", callback_data=f"delete#{id}"),
                    ],
                )
            else:
                list2 += (
                    [
                        InlineKeyboardButton(
                            result["title"], callback_data=f"send#{id}#{query.message.chat.id}"
                        ),
                    ],
                )

            if len(list2) >= RESULTS_COUNT:
                break

        list2.append(
            [
                InlineKeyboardButton(
                    text="NEXT ⏩", callback_data=f"next_{int(offset/10)+1}_{keyword}"
                )
            ],
        )

        if int((offset / 10) + 1) == 0:

            list2.append(
                [
                    InlineKeyboardButton(
                        text="BACK", callback_data=f"back_{int(offset/10)-1}_{keyword}"
                    )
                ],
            )

        list2.append(
            [
                InlineKeyboardButton(
                    text=f"📃 Pages {int((offset/10)+1)} / {math.ceil(len(results) / 10)}",
                    callback_data="pages",
                )
            ],
        )

        reply_markup = InlineKeyboardMarkup(list2)
        txt = await query.edit_message_caption(
            caption=f"Results for {keyword}", reply_markup=reply_markup
        )
