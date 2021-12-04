from pyrogram import Client, filters
from utils import save_file
from info import CHANNELS

media_filter = filters.document | filters.text | filters.video | filters.audio


@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Media Handler"""
    for file_type in ("document", "video", "audio", "text"):
        if file_type=="text":
            word=message.text
        elif word==0:
            break
        else:
            media = getattr(message, file_type, None)
            if media is not None:
                break
    else:
        return

    media.file_type = word
    media.caption = message.caption
    await save_file(media)
    word=0
