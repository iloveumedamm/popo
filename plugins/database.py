from datetime import datetime
import time
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB, DATABASE_NAME, COLLECTION_NAME

client = AsyncIOMotorClient(MONGODB)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
users = db.users


async def add_user(user_id):
    res = {
        "user_id": user_id,
    }
    already_exist = await users.find_one({"user_id": user_id})
    if not already_exist:
        return await users.insert_one(res)


async def find_user(user_id):
    await users.find_one({"user_id": user_id})


async def get_all_users():
    return users.find({})


async def delete_user(user_id):
    return await users.delete_one({"user_id": user_id})


async def get_total_users():
    return await users.count_documents({})


async def add_file(unique_id, caption, title, thumbnail):
    res = {
        "caption": caption,
        "title": title,
        "unique_id": unique_id,
        "thumbnail": thumbnail,
    }
    already_exist = await collection.find_one({"unique_id": unique_id, "caption": caption})
    if not already_exist:
        return await collection.insert_one(res)


class GroupDatabase:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.grp = self.db.groups

    def new_group(self, id):
        return dict(
            id=id,
            shortener_api=None,
            shortener_domain=None,
            falcon_api=None,
            access_days=12546,
            last_verified=datetime(2020, 5, 17),
            fsub=False,
            fsub_channel=0,
            has_access=True,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )

    async def add_group(self, id):
        group = self.new_group(id)
        return await self.grp.insert_one(group)

    async def get_group(self, id):
        if not await self.grp.find_one({"id": id}):
            await self.add_group(id)

        return await self.grp.find_one({"id": id})

    async def find_chat(self, id):
        return await self.get_group(id)

    async def find_chat_without_adding(self, id):
        return await self.grp.find_one({"id": id})

    async def update_group_info(self, group_id, value: dict, tag="$set"):
        myquery = {"id": group_id}
        newvalues = {tag: value}
        await self.grp.update_one(myquery, newvalues)

    async def is_group_verified(self, group_id):
        group = await self.find_chat(group_id)
        access_days = datetime.fromtimestamp(time.mktime(
            group["last_verified"].timetuple()) + group['access_days'])
        return (access_days - datetime.now()).total_seconds() >= 0

    async def expiry_date(self, group_id):
        group = await self.find_chat(group_id)
        access_days = datetime.fromtimestamp(time.mktime(
            group["last_verified"].timetuple()) + group['access_days'])
        return access_days, int((access_days - datetime.now()).total_seconds())

    async def total_premium_groups_count(self):
        return await self.grp.count_documents({"has_access": True, "chat_status.is_disabled": False})

    async def filter_chat(self, value):
        return self.grp.find(value)

    async def get_all_groups(self):
        return self.grp.find({})

    async def total_groups_count(self):
        return await self.grp.count_documents({})

group_db = GroupDatabase(MONGODB, DATABASE_NAME)

########################################################
client = AsyncIOMotorClient(MONGODB)
mydb = client[DATABASE_NAME]

class Database:
    default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
    }

    def __init__(self):
        self.col = mydb.Users
        self.grp = mydb.Groups
        self.users = mydb.uersz
       
    async def get_verify_status(self, user_id):
        user = await self.col.find_one({'id':int(user_id)})
        if user:
            return user.get('verify_status', self.default_verify)
        return self.default_verify
        
    async def update_verify_status(self, user_id, verify):
        await self.col.update_one({'id': int(user_id)}, {'$set': {'verify_status': verify}})

db = Database()
    