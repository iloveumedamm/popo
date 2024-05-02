import asyncio
import logging
import re, random, string
import time
import datetime
from pyrogram.errors import UserNotParticipant
from bson.objectid import ObjectId
from pymongo import TEXT
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.errors import ChannelInvalid
from config import *
from config import FORCESUB, UPDATE_CHANNEL, WELCOME_IMAGE, LOG_CHANNEL
from helpers.auto_delete import auto_delete
from helpers.shortener import mdisk_droplink_convertor
from plugins.database import collection, group_db, db
from plugins.forcesub import forcesub_handler, groups_lele
from translation import *
from utils import (force_sub_func, get_group_info_button, get_group_info_text,
                   group_admin_check, is_bot_admin, is_premium_group)

from .database import add_user, collection, find_user, get_total_users
from utils import get_verify_status, update_verify_status, get_readable_time, temp, get_shortlink

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@Client.on_callback_query(filters.regex('home'))
@Client.on_message(filters.command('start'))
async def start_message(c,m):
    if not await find_user(m.from_user.id):
        await add_user(m.from_user.id)

    if isinstance(m, CallbackQuery):
        await m.message.delete()
        m = m.message
        m.command = ["start"]

    collection.create_index([("title" , TEXT),("caption", TEXT)],name="movie_index")
    if len(m.command) == 1:
        return await m.reply_photo(WELCOME_IMAGE,
            caption=START_MESSAGE.format(m.from_user.mention),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("➕ Add Me To Your Groups ➕", url=f'http://t.me/{c.raw_username}?startgroup=true'),
                    ],
                    [
                        InlineKeyboardButton("ʙᴇsᴛ ᴜʀʟ sʜᴏʀᴛɴᴇʀ", url=f'https://t.me/MdiskShortner_Link'),
                    ],
                    [ 
                        InlineKeyboardButton("ℹ️ Help", callback_data="help") ,
                        InlineKeyboardButton("📢 About", callback_data="about")

                    ]
                ],

            )
        )
    else:
        if "group_link" in m.text:
            if not await groups_lele(c, m):
             return


   # if FORCESUB == 'True' and not await forcesub_handler(c, m):
    #    return
    
    group_id =  m.command[1].split("_")[2] if len(m.command) > 1 else m.chat.id
    group_id = int(group_id)
    group_config = await group_db.find_chat_without_adding(group_id)
    is_premium = (await group_db.is_group_verified(group_id)) or not PAID

#API_KEY = {user["shortener_api"] if user["shortener_api"] else Telegram.API_KEY
    verify_status = await get_verify_status(m.from_user.id)
    if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
        await update_verify_status(m.from_user.id, is_verified=False)

    mc = m.command[1]
    if mc.startswith('verify'):
        _, token = mc.split("_", 1)
        verify_status = await get_verify_status(m.from_user.id)
        if verify_status['verify_token'] != token:
            return await m.reply("Your verify token is invalid.")
        await update_verify_status(m.from_user.id, is_verified=True, verified_time=time.time())
        if verify_status["link"] == "":
            reply_markup = None
        else:
            btn = [[
                InlineKeyboardButton("📌 Get File 📌", url=f'https://t.me/{temp.U_NAME}?start={verify_status["link"]}')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
        await m.reply(f"✅ You successfully verified until: {get_readable_time(VERIFY_EXPIRE)}", reply_markup=reply_markup, protect_content=True)
        return
    
    verify_status = await get_verify_status(m.from_user.id)
    if IS_VERIFY and not verify_status['is_verified']:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await update_verify_status(m.from_user.id, verify_token=token, link="" if mc == 'inline_verify' else mc)
            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://t.me/{temp.U_NAME}?start=verify_{token}')
            btn = [[
                InlineKeyboardButton("🧿 Verify 🧿", url=link)
            ],[
                InlineKeyboardButton('🗳 Tutorial 🗳', url=VERIFY_TUTORIAL)
            ]]
            await m.reply("You not verified today! Kindly verify now. 🔐", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
            return
    else:
        pass        

        shortener_domain = group_config['shortener_domain'] if group_config['shortener_domain'] else SHORTENER_WEBSITE
        shortener_api = group_config['shortener_api'] if group_config['shortener_api'] else SHORTENER_API

        force_sub = group_config.get("fsub", False)
        force_sub_channel = group_config.get("fsub_channel", None)
        _id = m.command[1].split("_")[1]
        if is_premium and force_sub and force_sub_channel:
            is_joined = await force_sub_func(c, force_sub_channel, m, _id, group_id)

            if is_joined is not True:
                return

        result = await collection.find_one({"_id": ObjectId(_id)})

        try:
            caption = result["caption"]
        except Exception as e:
            return await m.reply("Some error occurred {e}")

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
            if m.chat.id in ADMINS
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
        caption = await mdisk_droplink_convertor(caption, shortener_domain, shortener_api)
        caption = CUSTOM_CAPTION.format(caption=caption)
        text = await m.reply_photo(
                caption=caption, photo=result["thumbnail"], reply_markup=reply_markup
            )

        await auto_delete(text)

#@Client.on_message(filters.command('group_link') & filters.private & filters.incoming)
async def group_link(c,m):
    owner = await c.get_users(int(OWNER_ID))
    if FILMS_LINK:
        try:
            user = await c.get_chat_member(FILMS_LINK, m.from_user.id)
            if user.status == "kicked":
                await m.reply_text("**Hey you are banned 😜**\nfor more details contact {owner.mention(style='md')", quote=True)
                return
        except UserNotParticipant:
            sender_name = m.from_user.first_name
            invite_link = await c.create_chat_invite_link(chat_id=FILMS_LINK, name=sender_name, expire_date=datetime.datetime.now() + datetime.timedelta(hours=1))
            buttons = [[InlineKeyboardButton(text='Group Link', url=invite_link.invite_link), InlineKeyboardButton("🔄 Refresh 🔄", callback_data=f"sub_refresh#{FILMS_LINK}"),]]

            await m.reply_text(
                f"Hey {m.from_user.mention(style='md')} join movies group fast\n\n"
                "__Press the Following Button to join movies group Now 👇__",
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True,
                quote=True
            )
            return
        except Exception as e:
            print(e)
            await m.reply_text(f"Something Wrong. Please try again later or contact {owner.mention(style='md')}", quote=True)
            return

    return True

@Client.on_callback_query(filters.regex('help'))
@Client.on_message(filters.command('help') & (filters.private | filters.group) & filters.incoming)
async def help_message_cmd(c,m):
    if isinstance(m, CallbackQuery):
        await m.message.delete()
        m = m.message

    text = HELP_MESSAGE if m.from_user.id not in ADMINS else HELP_MESSAGE_ADMIN
    markup = InlineKeyboardMarkup( [[ InlineKeyboardButton("🔙 Back", callback_data="home") ]] )
    await m.reply_text(text, reply_markup=markup, disable_web_page_preview=True)


@Client.on_callback_query(filters.regex('about'))
@Client.on_message(filters.command('about') & (filters.private | filters.group) & filters.incoming)
async def about_message(c,m):

    if isinstance(m, CallbackQuery):
        await m.message.delete()
        m = m.message

    text = ABOUT_MESSAGE
    markup = InlineKeyboardMarkup( [[ InlineKeyboardButton("🔙 Back", callback_data="home") ]] )
    await m.reply_text(text, reply_markup=markup, disable_web_page_preview=True)

@Client.on_callback_query(filters.regex('buy'))
@Client.on_message(filters.command('buy') & (filters.private | filters.group) & filters.incoming)
async def buy_message(c,m):
        if isinstance(m, CallbackQuery):
            await m.message.delete()
            m = m.message
        owner = c.owner.username
        
        text = f"Contact @{owner} for subscription details"
        markup = InlineKeyboardMarkup( [[ InlineKeyboardButton("🔙 Back", callback_data="home") ]] )
        await m.reply_text(text, reply_markup=markup, disable_web_page_preview=True)

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


@Client.on_message(filters.command('set_site') & filters.group)
async def set_api(client: Client, message):

    userid = message.from_user.id if message.from_user else None
    grp_id = message.chat.id

    if not userid:
        return await message.reply("You are anonymous admin")

    if not await group_admin_check(client=client, message=message, userid=userid):
        return

    try:
        is_premium = await is_premium_group(grp_id)
    except Exception as e:
        logger.error(e)

    if not is_premium and PAID:
        await message.reply("Your group is not a premium group. Request access to this group by /request")
        return

    sts = await message.reply("Checking site")
    if len(message.command) < 2:
        return await sts.edit("No Input!!\n\n`/set_site site`\n\nFor example: /set_site  bzearn.com")

    elif len(message.command) == 2:
        api = message.command[1]

        await group_db.update_group_info(grp_id, {"shortener_domain": api})
        return await sts.edit("SITE has been set")


@Client.on_message(filters.command('api') & filters.group)
async def api_cmd_handler(client: Client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are anonymous admin")

    grp_id = message.chat.id
    
    if not await group_admin_check(client=client, message=message, userid=userid):
        return

    if not await is_premium_group(grp_id) and PAID:
        await message.reply("Your group is not a premium group. Request access to this group by /request")
        return

    sts = await message.reply("Checking...")
    group_info = await group_db.find_chat(grp_id)

    text = f"""
**Shortener Site:** `{group_info["shortener_domain"] or None}`
**Shortener API:** `{group_info["shortener_api"] or None}`
"""

    await sts.edit(text)


@Client.on_message(filters.command('set_shortener') & filters.group)
async def set_shortener(client: Client, message):
    userid = message.from_user.id if message.from_user else None
    grp_id = message.chat.id

    if not userid:
        return await message.reply("You are anonymous admin")

    if not await group_admin_check(client=client, message=message, userid=userid):
        return

    try:
        is_premium = await is_premium_group(grp_id)
    except Exception as e:
        logger.error(e)

    if not is_premium and PAID:
        await message.reply("Your group is not a premium group. Request access to this group by /request")
        return

    sts = await message.reply("Checking api")
    if len(message.command) < 2:
        return await sts.edit("No Input!!\n\n`/set_shortener api`\n\nFor example: /set_shortener  26261hdnd772712h1b")

    elif len(message.command) == 2:
        api = message.command[1]

        await group_db.update_group_info(grp_id, {"shortener_api": api})
        return await sts.edit("API has been set")


@Client.on_message(filters.command('premium_groups') & filters.private & filters.user(ADMINS))
async def premium_group_cmd(bot: Client, m):
    premium_groups = await group_db.filter_chat({"has_access":True, "chat_status.is_disabled":False})
    total_premium_groups = await group_db.total_premium_groups_count()
    text = f"List of premium groups - Total {total_premium_groups} groups\n\n"
    bin_text = ""

    async for group in premium_groups:
        try:
            if await is_premium_group(group["id"]):
                tg_group = await bot.get_chat(group["id"])
                bin_text += " `{group_id}` {group_link}\n".format(group_id=group["id"], group_link=tg_group.invite_link)
        except Exception as e:
            logger.error(e)

    bin_text = bin_text or "None"
    await m.reply(text+bin_text)


@Client.on_message(filters.command('myplan') & (filters.group | filters.private))
async def myplan_cmd_handler(bot, m):
    try:
        if len(m.command) == 1 and m.from_user.id in ADMINS:
            return await m.reply_text("`/myplan id`")

        if not await group_admin_check(client=bot, message=m, userid=m.from_user.id):
            return

        group_id = int(m.command[1]) if m.from_user.id in ADMINS else m.chat.id

        btn = await get_group_info_button(group_id)
        text = await get_group_info_text(bot, group_id)
        await m.reply(text, reply_markup=InlineKeyboardMarkup(btn) if m.from_user.id in ADMINS else None)

    except (ChannelInvalid, ValueError):
        await m.reply("Bot is not a admin of given group")
        return
        
    except Exception as e:
        logger.error(e, exc_info=True)


@Client.on_message(filters.command('request') & filters.group)
async def request_cmd_handler(bot: Client, m):

    if not await group_admin_check(client=bot, message=m, userid=m.from_user.id):
        return
    
    if PAID: 
        owner= (await bot.get_users(OWNER_ID)).mention 
        await m.reply(f"Contact {owner} to get access")

    else:
        await m.reply("This bot is free for all")



@Client.on_message(filters.command('fsub') & filters.group)
async def fsub_cmd_handler(bot: Client, message: Message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are anonymous admin")

    grp_id = message.chat.id
    
    if not await group_admin_check(client=bot, message=message, userid=userid):
        return

    if not await is_premium_group(grp_id) and PAID:
        await message.reply("Your group is not a premium group. Request access to this group by /request")
        return

    sts = await message.reply("Checking...")
    group_info = await group_db.find_chat(grp_id)

    text = f"""
**Current Status:** `{group_info.get("fsub") or None}`
**Current Channel:**  `{group_info.get("fsub_channel") or None}`"""

    await sts.edit(text)

@Client.on_message(filters.command('set_fsub') & filters.group)
async def fsub_channel(c, m):
    userid = m.from_user.id if m.from_user else None
    if not userid:
        return await m.reply("You are anonymous admin")

    grp_id = m.chat.id
    
    if not await group_admin_check(client=c, message=m, userid=userid):
        return

    if not await is_premium_group(grp_id) and PAID:
        await m.reply("Your group is not a premium group. Request access to this group by /request")
        return

    sts = await m.reply("Checking...")
    invalid_input_text = "Invalid Input!!\n\n`/set_fsub channel`\n\nFor example: `/set_fsub -100xxxxx`, to remove `/set_fsub 0`\n\nOR `/set_fsub True/False`"
    if len(m.command) < 2:
        return await sts.edit(invalid_input_text)

    elif len(m.command) == 2:

        if m.command[1].replace("-", "").isdigit():
            value =int( m.command[1])

            bot_admin = await is_bot_admin(c, value)
            if not bot_admin:
                await m.reply(f"Make {c.username} admin in given channel {value}")
                await sts.delete()
                return
            
            key = "fsub_channel"
        elif m.command[1] in ["True", "False"]:
            value = m.command[1] == "True"
            key = "fsub"
        else:
            return await sts.edit(invalid_input_text)

        await group_db.update_group_info(grp_id, {key: value})
        return await sts.edit("Settings has been set")
    

@Client.on_message(filters.command('total_groups') & filters.private & filters.user(ADMINS))
async def total_groups_cmd(bot: Client, m):
    total_groups = await group_db.total_groups_count()
    await m.reply(f"Total groups: **{total_groups}**\n\nTotal premium groups: **{await group_db.total_premium_groups_count()}**")



@Client.on_message(filters.command('total_users') & filters.private & filters.user(ADMINS))
async def total_users_cmd(bot: Client, m):
    total_users = await get_total_users()
    await m.reply(f"Total users: **{total_users}**")
