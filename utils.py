import asyncio
import logging
from config import ADMINS, PAID, VALIDITY
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from plugins.database import group_db
from collections import OrderedDict
from pyrogram.errors import UserNotParticipant
import pytz
import random 
import re
from shortzy import Shortzy
import os
from datetime import datetime, timedelta, date, time
import string
from plugins.database import collection, group_db, db
TOKENS = {}
VERIFIED = {}
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class temp(object):
    VERIFICATIONS = {}
    U_NAME = {}
    
async def group_admin_check(client, userid, message):

    if userid in ADMINS:
        return True

    grp_id = message.chat.id
    st = await client.get_chat_member(grp_id, userid)
    if st.status not in [
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ]:
        return

    return True


async def get_group_admins(client: Client, group_id):
    administrators = []
    async for m in client.get_chat_members(group_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        None if m.user.is_bot else administrators.append(m.user.id)

    return administrators

async def get_group_info_text(client, group_id: int):

    if not PAID:
        return "This bot is free for all, you can use it without any restrictions"
    
    txt = """**User ID:** `{group_id}`
**Group Link:** {group_link}
**Subscription Date:** `{subscription_date}`
**Expiry Date:** `{expiry_date}`
**Subscription Peroid Remaining:** `{time_remaining}`
**Banned:** `{banned_status}`
    """

    group = await group_db.find_chat(group_id)
    expiry_date_str, time_remaining = await group_db.expiry_date(group_id)
    subscription_date = group['last_verified'] if group["has_access"] else None

    if group["has_access"] == False or not await group_db.is_group_verified(group_id):
        await group_db.update_group_info(group_id, {"has_access": False})
        subscription_date = expiry_date_str = time_remaining = "Expired"

    tg_group = await client.get_chat(group_id)
    return txt.format(
        group_id=group_id,
        group_link=tg_group.invite_link,
        subscription_date=subscription_date,
        expiry_date=expiry_date_str,
        time_remaining=human_time(time_remaining)
        if type(time_remaining) is int
        else time_remaining,
        banned_status=group["chat_status"]["is_disabled"],
    )


async def get_group_info_button(group_id: int):
    btn = [[InlineKeyboardButton(text=f"Add {human_time(time_in_s)}", callback_data=f'validity#{group_id}#{time_in_s}')] for time_in_s in VALIDITY]
    btn.append([InlineKeyboardButton("Remove access", callback_data=f"removeaccess#{group_id}")])
    btn.append([InlineKeyboardButton("Close", callback_data="delete")])
    return btn


async def is_premium_group(group_id):
    return bool(await group_db.is_group_verified(group_id))

INTERVALS = OrderedDict([
    ('millennium', 31536000000),  # 60 * 60 * 24 * 365 * 1000
    ('century', 3153600000),      # 60 * 60 * 24 * 365 * 100
    ('year', 31536000),           # 60 * 60 * 24 * 365
    ('month', 2627424),           # 60 * 60 * 24 * 30.41 (assuming 30.41 days in a month)
    ('week', 604800),             # 60 * 60 * 24 * 7
    ('day', 86400),               # 60 * 60 * 24
    ('hour', 3600),               # 60 * 60
    ('minute', 60),
    ('second', 1)
])


def human_time(seconds, decimals=1):
    '''Human-readable time from seconds (ie. 5 days and 2 hours).
    Examples:
        >>> human_time(15)
        '15 seconds'
        >>> human_time(3600)
        '1 hour'
        >>> human_time(3720)
        '1 hour and 2 minutes'
        >>> human_time(266400)
        '3 days and 2 hours'
        >>> human_time(-1.5)
        '-1.5 seconds'
        >>> human_time(0)
        '0 seconds'
        >>> human_time(0.1)
        '100 milliseconds'
        >>> human_time(1)
        '1 second'
        >>> human_time(1.234, 2)
        '1.23 seconds'
    Args:
        seconds (int or float): Duration in seconds.
        decimals (int): Number of decimals.
    Returns:
        str: Human-readable time.
    '''
    if seconds < 0 or seconds != 0 and not 0 < seconds < 1 and 1 < seconds < INTERVALS['minute']:
        input_is_int = isinstance(seconds, int)
        return f'{str(seconds if input_is_int else round(seconds, decimals))} seconds'
    elif seconds == 0:
        return '0 seconds'
    elif 0 < seconds < 1:
        # Return in milliseconds.
        ms = int(seconds * 1000)
        return '%i millisecond%s' % (ms, 's' if ms != 1 else '')
    res = []
    for interval, count in INTERVALS.items():
        quotient, remainder = divmod(seconds, count)
        if quotient >= 1:
            seconds = remainder
            if quotient > 1:
                # Plurals.
                if interval == 'millennium':
                    interval = 'millennia'
                elif interval == 'century':
                    interval = 'centuries'
                else:
                    interval += 's'
            res.append('%i %s' % (int(quotient), interval))
        if remainder == 0:
            break

    return f'{res[0]} and {res[1]}' if len(res) >= 2 else res[0]


async def is_bot_admin(c, channel_id):
    if channel_id:
        try:
            await c.create_chat_invite_link(channel_id)
            return True
        except Exception as e:
            return
    return True


async def auto_delete_func(m, auto_delete_time):
    await asyncio.sleep(auto_delete_time)
    await m.delete()


async def force_sub_func(c, channel_id, m, file_id=0, group_id=0):
    owner = c.owner
    if not channel_id:
        return True

    invite_link = await c.create_chat_invite_link(channel_id)
    try:
        user = await c.get_chat_member(channel_id, m.from_user.id)
        if user.status == "kicked":
            return await m.reply_text("**Hey you are banned 😜**", quote=True)
    except UserNotParticipant:
        buttons = [
            [
                InlineKeyboardButton(
                    text="Updates Channel 🔖", url=invite_link.invite_link
                ),
            ]
        ]

        buttons.append(
            [
                InlineKeyboardButton(
                    text="🔄 Refresh 🔄",
                    callback_data=f"sub_refresh#{file_id}#{group_id}",
                )
            ]
        )

        return await m.reply_text(
            f"Hey {m.from_user.mention(style='md')} you need join My updates channel in order to use me 😉\n\n"
            "Press the Following Button to join Now 👇",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True,
        )
    except Exception as e:
        print(e)
        return await m.reply_text(
            f"Something Wrong. Please try again later or contact {owner.mention(style='md')}",
            quote=True,
        )
    return True


async def get_verify_status(user_id):
    verify = temp.VERIFICATIONS.get(user_id)
    if not verify:
        verify = await db.get_verify_status(user_id)
        temp.VERIFICATIONS[user_id] = verify
    return verify

async def update_verify_status(user_id, verify_token="", is_verified=False, verified_time=0, link=""):
    current = await get_verify_status(user_id)
    current['verify_token'] = verify_token
    current['is_verified'] = is_verified
    current['verified_time'] = verified_time
    current['link'] = link
    temp.VERIFICATIONS[user_id] = current
    await db.update_verify_status(user_id, current)
    
def get_readable_time(seconds):
    periods = [('d', 86400), ('h', 3600), ('m', 60), ('s', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result

    
async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""

        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1

        unit = ts[index:]

        if value:
            value = int(value)

        return value, unit

    value, unit = extract_value_and_unit(time_string)

    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0    
    
async def get_shortlink(url, api, link):
    shortzy = Shortzy(api_key=api, base_site=url)
    link = await shortzy.convert(link)
    return link    