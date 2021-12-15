import datetime
from info import DATABASE_NAME, DATABASE_URI, Channel
from database import user_status

db = Database(DATABASE_URI, DATABASE_NAME)


async def handle_user_status(bot, cmd):
    chat_id = cmd.from_user.id
    if not await db.is_user_exist(chat_id):
        await db.add_user(chat_id)
        await bot.send_message(
            Channel,
            f"#NEW_USER: \n\nNew User [{cmd.from_user.first_name}](tg://user?id={cmd.from_user.id}) started SWAHILI_HIT ROBOT !!"
        )

    ban_status = await db.get_ban_status(chat_id)
    if ban_status["is_banned"]:
        if (
                datetime.date.today() - datetime.date.fromisoformat(ban_status["banned_on"])
        ).days > ban_status["ban_duration"]:
            await db.remove_ban(chat_id)
        else:
            await cmd.reply_text("You are Banned to Use This Bot 🥺", quote=True)
            return
    await cmd.continue_propagation()
