
import asyncio
import datetime
import logging
import random
import string
import time
import traceback

import aiofiles
import aiofiles.os
from .database import group_db
from utils import human_time
from pyrogram import Client, filters
from pyrogram.errors import (FloodWait, PeerIdInvalid)
from pyrogram.types import Message

from config import ADMINS, OWNER_ID, SUBSCRIPTION_REMINDER_MESSAGE
from utils import get_group_admins


broadcast_ids = {}

@Client.on_message(filters.command("premium_reminder") & filters.private & filters.user(ADMINS))
async def reminder_handler(c:Client, m:Message):
    try:
        await main_reminder_handler(c, m)
    except Exception as e:
        logging.error("Failed to execute reminder", exc_info=True)


async def send_msg(group_id, msg, client: Client):
    try:
        admins = await get_group_admins(client, group_id)
        for user_id in admins:
            await client.send_message(user_id, msg)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(group_id, msg, client)
    except PeerIdInvalid:
        return 400, f"{group_id} : group id invalid\n"
    except Exception as e:
        return 500, f"{group_id} : {traceback.format_exc()}\n"


async def main_reminder_handler(client: Client, m: Message):
    all_groups = await group_db.filter_chat({"has_access":True, "chat_status.is_disabled":False})

    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for _ in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(text="Reminder Message Started Sending to groups! You will be notified with log file when all the groups are notified.")

    start_time = time.time()
    total_groups = await group_db.total_premium_groups_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(total=total_groups , current=done, failed=failed, success=success)
    owner_mention = (await client.get_users(OWNER_ID)).mention
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for group in all_groups:
            expiry_date_str, time_remaining = await group_db.expiry_date(group["id"])

            if time_remaining <= 172800:
                subscription_date = group['last_verified'] if group["has_access"] else None
                if not await group_db.is_group_verified(group["id"]):
                    await group_db.update_group_info(group["id"], {"has_access": False})
                    subscription_date = expiry_date_str = time_remaining = "Expired"
                tg_group = await client.get_chat(group["id"])

                text = SUBSCRIPTION_REMINDER_MESSAGE.format(
                                        group_id=group["id"], 
                                        group_link=tg_group.invite_link,
                                        subscription_date=subscription_date, 
                                        expiry_date=expiry_date_str, 
                                        time_remaining=human_time(time_remaining) if type(time_remaining) is int else time_remaining , 
                                        banned_status=group["chat_status"]["is_disabled"],
                                        owner=owner_mention)

                sts, msg = await send_msg(int(group['id']), text, client=client)
                if msg is not None:
                    await broadcast_log_file.write(msg)
                if sts == 200:
                    success += 1
                else:
                    failed += 1
                done += 1
                if broadcast_ids.get(broadcast_id) is None:
                    break
                else:
                    broadcast_ids[broadcast_id].update(dict(current=done, failed=failed, success=success))

    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await asyncio.sleep(3)
    await out.delete()
    if failed == 0:
        await m.reply_text(text=f"Reminder Notification completed in `{completed_in}`\n\nTotal groups {total_groups}.\nTotal done {done}, {success} success and {failed} failed.", quote=True)

    else:
        await m.reply_document(document='broadcast.txt', caption=f"Reminder Notification completed in `{completed_in}`\n\nTotal groups {total_groups}.\nTotal done {done}, {success} success and {failed} failed.", quote=True)

    await aiofiles.os.remove('broadcast.txt')
