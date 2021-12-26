import logging
from pyrogram import Client, emoji, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument,InlineQueryResultPhoto

from utils import get_search_results, is_subscribed, get_size
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME

BOT = {}
@Client.on_inline_query(filters.user(AUTH_USERS) if AUTH_USERS else None)
async def answer(bot, query):
    """Show search results for given inline query"""
    nyva=BOT.get("username")
    if not nyva:
        botusername=await bot.get_me()
        nyva=botusername.username
        BOT["username"]=nyva
    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='You have to subscribe my channel to use the bot',
                           switch_pm_parameter="subscribe")
        return

    results = []
    if '|' in query.query:
        string, file_type = query.query.split('|', maxsplit=1)
        string = string.strip()
        file_type = file_type.strip().lower()
    else:
        string = query.query.strip()
        file_type = None

    offset = int(query.offset or 0)
    files, next_offset = await get_search_results(string,
                                                  file_type=file_type,
                                                  max_results=10,
                                                  offset=offset)

    for file in files:
        title = file.file_name.split('.dd#.')[1]
        descp = file.file_name.split('.dd#.')[0]
        id2 = file.file_name.split('.dd#.')[2]
        size=get_size(file.file_size)
        f_caption=file.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
            except Exception as e:
                print(e)
                f_caption=f_caption
        if f_caption is None:
            f_caption = f"{title}"
        if id2=='x':
            if file.file_type != "photo":
                reply_markup=get_reply_markup(string,file.file_id,nyva)
                results.append(
                    InlineQueryResultCachedDocument(
                        title=title,
                        file_id=file.file_id,
                        caption=f_caption,
                        description=f'{descp}',
                        reply_markup=reply_markup))
            else:
                reply_markup=get_reply_markup(string,file.file_id,nyva)
                results.append(InlineQueryResultPhoto(
                        photo_url = file.file_id,
                        title=title,
                        description= descp,
                        caption=f_caption,
                        reply_markup=reply_mark_up))      
    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} Results"
        if string:
            switch_pm_text += f" for {string}"

        try:
            await query.answer(results=results,
                           is_personal = True,
                           cache_time=cache_time,
                           switch_pm_text=switch_pm_text,
                           switch_pm_parameter="start",
                           next_offset=str(next_offset))
        except Exception as e:
            logging.exception(str(e))
            await query.answer(results=[], is_personal=True,
                           cache_time=cache_time,
                           switch_pm_text=str(e)[:63],
                           switch_pm_parameter="error")
    else:

        switch_pm_text = f'{emoji.CROSS_MARK} No results'
        if string:
            switch_pm_text += f' for "{string}"'

        await query.answer(results=[],
                           is_personal = True,
                           cache_time=cache_time,
                           switch_pm_text=switch_pm_text,
                           switch_pm_parameter="okay")


def get_reply_markup(query, file_id, nyva):
    buttons = [
        [
            InlineKeyboardButton('📤 Download', url=f"https://telegram.dog/{nyva}?start=subinps_-_-_-_{file_id}")
        ]
        ]
    return InlineKeyboardMarkup(buttons)
