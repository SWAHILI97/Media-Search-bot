import datetime
import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI


class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
    def new_group(self, id, title , total, link,id2):
        return dict(
            id = id,
            user_id = id2,
            title = title,
            link_inv = link,
            total_m = total
        )

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            first_time=True,
            paid_id = 0,
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason=''
            )
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def add_group(self, id,title,total,link,id2):
        group = self.new_group(id,title,total,link,id2)
        await self.grp.insert_one(group)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return True if user else False

    async def is_group_exist(self, id):
        title = 2
        user = await self.grp.find_one({'id': id})
        if not user:
            return False,title
        return (True if user else False),int(user["user_id"])

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def total_group_count(self):
        count = await self.grp.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def delete_group(self, group_id):
        await self.grp.delete_many({'id': int(group_id)})

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})

    async def ban_user(self, user_id, ban_duration, ban_reason):
        ban_status = dict(
            is_banned=True,
            ban_duration=ban_duration,
            banned_on=datetime.date.today().isoformat(),
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason=''
        )
        user = await self.col.find_one({'id': int(id)})
        return user.get('ban_status', default)

    async def get_all_banned_users(self):
        banned_users = self.col.find({'ban_status.is_banned': True})
        return banned_users


db = Database(DATABASE_URI, DATABASE_NAME)
