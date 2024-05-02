import base64
import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
from config import *
from plugins.database import add_user, find_user

@Client.on_message(filters.private & filters.incoming)
async def forcesub(c, m):
    if FORCESUB == 'True' and not await forcesub_handler(c, m):
        return
    await m.continue_propagation()



async def forcesub_handler(c,m): 
    owner = await c.get_users(int(OWNER_ID))
    if UPDATE_CHANNEL:
        try:
            user = await c.get_chat_member(UPDATE_CHANNEL, m.from_user.id)
            if user.status == "kicked":
                await m.reply_text("**Hey you are banned 😜**", quote=True)
                return
        except UserNotParticipant:
            sender_name = m.from_user.first_name
            invite_link = await c.create_chat_invite_link(chat_id=UPDATE_CHANNEL, name=sender_name, expire_date=datetime.datetime.now() + datetime.timedelta(hours=1))
            buttons = [[InlineKeyboardButton(text='Updates Channel 🔖', url=invite_link.invite_link), InlineKeyboardButton("🔄 Refresh 🔄", callback_data=f"sub_refresh#{UPDATE_CHANNEL}"),]]

            await m.reply_text(
                f"Hey {m.from_user.mention(style='md')} you need join My updates channel in order to use me 😉\n\n"
                "__Press the Following Button to join Now 👇__",
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            return
        except Exception as e:
            print(e)
            await m.reply_text(f"Something Wrong. Please try again later or contact {owner.mention(style='md')}", quote=True)
            return

    return True

    

async def groups_lele(c,m): 
    owner = await c.get_users(int(OWNER_ID))
    if FILMS_LINK:
        try:
            user = await c.get_chat_member(FILMS_LINK, m.from_user.id)
            if user.status == "kicked":
                await m.reply_text("**Hey you are banned 😜**", quote=True)
                return
        except UserNotParticipant:
            sender_name = m.from_user.first_name
            invite_link = await c.create_chat_invite_link(chat_id=FILMS_LINK, name=sender_name, expire_date=datetime.datetime.now() + datetime.timedelta(hours=1))
            buttons = [[InlineKeyboardButton(text='Updates Channel 🔖', url=invite_link.invite_link), InlineKeyboardButton("🔄 Refresh 🔄", callback_data=f"sub_refresh#{UPDATE_CHANNEL}"),]]

            await m.reply_text(
                f"Hey {m.from_user.mention(style='md')} you need join My updates channel in order to use me 😉\n\n"
                "__Press the Following Button to join Now 👇__",
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            return
        except Exception as e:
            print(e)
            await m.reply_text(f"Something Wrong. Please try again later or contact {owner.mention(style='md')}", quote=True)
            return

    return True

