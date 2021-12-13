import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from info import START_MSG, CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from utils import Media, get_file_details, get_size, save_file, get_filter_results
from pyrogram.errors import UserNotParticipant
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start"))
async def start(bot, cmd):
    usr_cmdall1 = cmd.text
    if usr_cmdall1.startswith("/start subinps"):
        if AUTH_CHANNEL:
            invite_link = await bot.create_chat_invite_link(int(AUTH_CHANNEL))
            try:
                user = await bot.get_chat_member(int(AUTH_CHANNEL), cmd.from_user.id)
                if user.status == "kicked":
                    await bot.send_message(
                        chat_id=cmd.from_user.id,
                        text="Sorry Sir, You are Banned to use me.",
                        parse_mode="markdown",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                ident, file_id = cmd.text.split("_-_-_-_")
                await bot.send_message(
                    chat_id=cmd.from_user.id,
                    text="**Please Join My Updates Channel to use this Bot!**",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("🤖 Join Updates Channel", url=invite_link.invite_link)
                            ],
                            [
                                InlineKeyboardButton(" 🔄 Try Again", callback_data=f"checksub#{file_id}")
                            ]
                        ]
                    ),
                    parse_mode="markdown"
                )
                return
            except Exception:
                await bot.send_message(
                    chat_id=cmd.from_user.id,
                    text="Something went Wrong.",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                )
                return
        try:
            ident, file_id = cmd.text.split("_-_-_-_")
            filedetails = await get_file_details(file_id)
            for files in filedetails:
                title = files.file_name
                size=get_size(files.file_size)
                f_caption=files.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
                    except Exception as e:
                        print(e)
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{files.file_name}"
            strg=files.file_name.split('.dd#.')[3]
            strgs = strg.split('.')[1]
            strg2 = strg.split('.')[0]
            link = files.file_name.split('.dd#.')[4]
            if filedetails:
                if strgs.lower() == 't':
                    await bot.send_message(
                        chat_id=cmd.from_user.id,
                        text="Something went Wrong"
                        )
                    
                if strg2.lower() == 'm':
                    buttns = [
                            [
                                 InlineKeyboardButton("DOWNLOAD",callback_data=f"subinps#{files.file_id}"),
                                 InlineKeyboardButton("GOOGLE LINK",url= link)
                            ]
                        ]
                    await bot.send_cached_media(
                        chat_id=cmd.from_user.id,
                        file_id=file_id,
                        caption=f_caption,
                        reply_markup=InlineKeyboardMarkup(buttns)
                        )
                elif strg2.lower() == 's':
                    filef=await get_filter_results(file_id)
                    output = []
                    output.append(InlineKeyboardButton("GOOGLE LINK",url= link))
                    for x in filef.file_name:
                        i= x.split('.d#.')[1]
                        if i not in output:
                            output.append(InlineKeyboardButton(f"{i}",callback_data=f"subinps#{x}" ))
                    buttons=list(split_list(output,2))
                    await bot.send_cached_media(
                        chat_id=cmd.from_user.id,
                        file_id=file_id,
                        caption=f_caption,
                        reply_markup=InlineKeyboardMarkup(buttons)
                        )
                    
        except Exception as err:
            await cmd.reply_text(f"Something went wrong!\n\n**Error:** `{err}`")
    elif len(cmd.command) > 1 and cmd.command[1] == 'subscribe':
        invite_link = await bot.create_chat_invite_link(int(AUTH_CHANNEL))
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text="**Please Join My Updates Channel to use this Bot!**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🤖 Join Updates Channel", url=invite_link.invite_link)
                    ]
                ]
            )
        )
    else:
        await cmd.reply_text(
            START_MSG,
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Search Here", switch_inline_query_current_chat=''),
                        InlineKeyboardButton("Other Bots", url="https://t.me/subin_works/122")
                    ],
                    [
                        InlineKeyboardButton("About", callback_data="about")
                    ]
                ]
            )
        )


@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot, message):
    """Show total files in database"""
    msg = await message.reply("Processing...⏳", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Saved files: {total}')
    except Exception as e:
        logger.exception('Failed to check total files')
        await msg.edit(f'Error: {e}')


@Client.on_message(filters.command('logger') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
    
    files = await get_filter_results(query=media.file_name)
    if files:
        for file in files: 
            title = file.file_name.split('.dd#.')[1]
            if title==media.file_name:
                result = await Media.collection.delete_one({
                    'file_name': file.file_name,
                    'file_size': media.file_size,
                    'mime_type': media.mime_type
                    })   
        if result.deleted_count:
            await msg.edit('File is successfully deleted from database')
        else:
            await msg.edit('File not found in database')
@Client.on_message(filters.command('about'))
async def bot_info(bot, message):
    buttons = [
        [
            InlineKeyboardButton('Update Channel', url='https://t.me/subin_works'),
            InlineKeyboardButton('Source Code', url='https://github.com/subinps/Media-Search-bot')
        ]
        ]
    await message.reply(text="Language : <code>Python3</code>\nLibrary : <a href='https://docs.pyrogram.org/'>Pyrogram asyncio</a>\nSource Code : <a href='https://github.com/subinps/Media-Search-bot'>Click here</a>\nUpdate Channel : <a href='https://t.me/subin_works'>XTZ Bots</a> </b>", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
@Client.on_message(filters.command('addposter') & filters.user(ADMINS))
async def add_poster(bot, message):
    """Media Handler"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file or video or audio with /addposter command to message you want to add to database', quote=True)
        return
    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            media.file_type = file_type
            media.caption = reply.caption
            break
    else:
        return
    
    resv = ".dd#.x"
    mk=await bot.ask(text = " send artist or DJ or else send haijatafsiriwa", chat_id = message.from_user.id)
    access = await bot.ask(text = " send access and type eg m.t that is movie and access true or s.t series true", chat_id = message.from_user.id)
    link = await bot.ask(text = " send link", chat_id = message.from_user.id)
    media.file_name = f'{mk.text}.dd#.{media.file_name}{resv}.dd#.{access.text}.dd#.{link.text}'
    replly,dta_id = await save_file(media)
    await mk.reply(f'{mk.text}\n caption {media.caption}\n type {media.file_type} \n {replly} with id {dta_id}')
   
@Client.on_message(filters.command('adddata') & filters.user(ADMINS))
async def add_data(bot, message):
    """Media Handler"""
    reply = message.reply_to_message
    pres = 'absent'
    if reply and reply.media:
        msg = await reply.reply("Processing...⏳", quote=True)
        for file_type in ("document", "video", "audio"):
            media = getattr(reply, file_type, None)
            if media is not None:
                break
        files = await get_filter_results(query=media.file_name)
        if files:
            for file in files: 
                title = file.file_name.split('.dd#.')[1]
                if title==media.file_name and file.file_size == media.file_size and file.mime_type == media.mime_type:
                    pres = 'present'
                    break  
        else:
            await msg.edit('file not found in database please try another file')
            return
        statusi = file.file_name.split('.dd#.')[2] 
        dcm_id = file.file_id     
        if statusi == 'x' and pres == 'present':
            dta = 'stat'
            dtb = 'stop'
            mkv = await bot.ask(text = " send batch name season(S01EP(1-10)) or else movie", chat_id = message.from_user.id)
            while dta!='stop':
                mk=await bot.ask(text = " send media or document or audio else send stop", chat_id = message.from_user.id)
                if mk.media:
                    for file_type in ("document", "video", "audio"):
                        media = getattr(mk, file_type, None)
                        if media is not None:
                            media.file_type = file_type
                            media.caption = mk.caption
                            break
                    resv = f'.dd#.{dcm_id}'
                    mkg = 'data.dd#.'
                    media.file_name = f'{mkg}{media.file_name}{resv}.d#.{mkv.text}'
                    a,b = await save_file(media)
                    await mkv.reply(f'{mkg}\n caption {media.caption}\n type {media.file_type} \n {a} to database')

                elif mk.text.lower()==dtb:
                    dta = 'stop'
                    await mk.reply(f'all file sent to database with id  {dcm_id}')
                    break
        else:
            await msg.reply("file not accessible in database", quote=True)
            return
    else:
        await message.reply('Reply to file or video or audio with /adddata command to message you want to add to database', quote=True)
        return

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    clicked = query.from_user.id
    try:
        typed = query.message.reply_to_message.from_user.id
    except:
        typed = query.from_user.id
        pass
    if (clicked == typed):
        if query.data.startswith("subinps"):
            ident, file_id = query.data.split("#")
            filez=await get_filter_results(file_id)
            for file in reversed(filez):
                filedetails = await get_file_details(file.file_id)
                for files in filedetails:
                    title = files.file_name
                    size=get_size(files.file_size)
                    f_caption=files.caption
                    if CUSTOM_FILE_CAPTION:
                        try:
                            f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
                        except Exception as e:
                            print(e)
                            f_caption=f_caption
                    if f_caption is None:
                        f_caption = f"{files.file_name}"
                    buttons = [
                        [
                            InlineKeyboardButton('More Bots', url='https://t.me/subin_works/122'),
                            InlineKeyboardButton('Update Channel', url='https://t.me/subin_works')
                        ]
                        ]
                
                    await query.answer()
                    await client.send_cached_media(
                        chat_id=query.from_user.id,
                        file_id=file_id,
                        caption=f_caption,
                        reply_markup=InlineKeyboardMarkup(buttons)
                        )

        
