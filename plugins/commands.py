import os
import logging
from plugins.channel import db
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from info import START_MSG, CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from utils import Media, get_file_details, get_size, save_file, get_filter_results,upload_photo
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
                ban_status = await db.get_ban_status(cmd.from_user.id)
                if strgs.lower() == 'f' or ban_status["is_banned"]:
                    if strg2.lower() == 'm':
                        buttns = [
                                [
                                    InlineKeyboardButton("📤 DOWNLOAD",callback_data=f"subinps.dd#.{files.file_id}")
                          
                                ],
                                [
                                    InlineKeyboardButton("🔗 GOOGLE LINK",url= link)
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
                        output.append(InlineKeyboardButton("🔗 GOOGLE LINK",url= link))
                        for x in filef:
                            i= x.file_name.split('.dd#.')[2]
                            a,b= i.split('.d#.')
                            l1,l2= a.split('@.')
                            dataa=InlineKeyboardButton(f"{b}",callback_data=f"subinps.dd#.{l1} {l2}" )
                            if dataa not in output:
                                output.append(dataa)
                        buttons=list(split_list(output,2))
                        await bot.send_cached_media(
                            chat_id=cmd.from_user.id,
                            file_id=file_id,
                            caption=f_caption,
                            reply_markup=InlineKeyboardMarkup(buttons)
                        )
                else:
                    await bot.send_message(
                        chat_id=cmd.from_user.id,
                        text=f"Samahani **{cmd.from_user.first_name}** nmeshindwa kukuruhusu kendelea kwa sababu muv au sizon uliochagua ni za kulipia\n Tafadhal chagua nchi uliopo kuweza kulipia kifurushi",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("🇹🇿 TANZANIA", callback_data = "tanzania"),
                                    InlineKeyboardButton("🇰🇪 KENYA",callback_data ="kenya" )
                                ]
                            ]
                        )
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
        return
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
    for file_type in ("document", "video", "audio" ,"photo"):
        media = getattr(reply, file_type, None)
        if media is not None and reply.photo:
            testi=k=await bot.ask(text = " send filename of the photo", chat_id = message.from_user.id)
            media.mime_type = "sfghhd"
            media.file_name = testi.text
            media.file_id = await upload_photo(bot,reply)
            media.file_type = file_type
            media.caption = reply.caption
            break
        elif media is not None :
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
            mkv = await bot.ask(text = " send batch name season start with last ep separate by hash e.g 10#(S01EP(1-10)) or else m#movie", chat_id = message.from_user.id)
            mkv1,mkv2 = mkv.text.split('#')
            while dta!='stop':
                mk=await bot.ask(text = " send media or document or audio else send stop", chat_id = message.from_user.id)
                if mk.media:
                    for file_type in ("document", "video", "audio"):
                        media = getattr(mk, file_type, None)
                        if media is not None:
                            media.file_type = file_type
                            media.caption = mk.caption
                            break
                    resv = f'{dcm_id}'
                    mkg = 'data.dd#.'
                    media.file_name = f'{mkg}{media.file_name}.dd#.H{mkv1}@.{resv}.d#.{mkv2}'
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
@Client.on_message(filters.private & filters.command("add_user") & filters.user(ADMINS))
async def ban(c,m):
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to add access to any user from the bot.\n\n"
            f"Usage:\n\n"
            f"`/add_user user_id duration_in days ofa_given`\n\n"
            f"Eg: `/add_user 1234567 28 Umepata ofa ya Siku 3 zaidi.`\n"
            f"This will add user with id `1234567` for `28` days for the reason `ofa siku 3 zaidi`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        ban_log_text = f"Adding user {user_id} for {ban_duration} days for the reason {ban_reason}."
        try:
            await c.send_message(
                user_id,
                f"Muamala wako tumeupokea sasa unaweza kupata huduma zetu za muv na sizon \n **🧰🧰 KIFURUSHI CHAKO 🧰🧰** \n🗓🗓**siku___siku{ban_duration}(+ofa)**\n🎁🎁ofa ___ ** __{ban_reason}__** \nkujua salio liliobaki tuma neno salio\n\n"
                f"**Message from the admin**"
            )
            ban_log_text += '\n\nUser notified successfully!'
        except:
            traceback.print_exc()
            ban_log_text += f"\n\nNmeshindwa kumtaarifu tafadhali karibu tena! \n\n`{traceback.format_exc()}`"

        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(
            ban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )
@Client.on_message((filters.private | filters.group) & filters.command('niunge'))
async def addconnection(client,message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Samahan wewe ni anonymous(bila kujulikana) admin tafadhali nenda kweny group lako edit **admin permission** remain anonymouse kisha disable jaribu tena kituma /niumge.\nAu kama unatak uendelee kuwa anonymous admin copy huu  ujumbe **__/niunge {message.chat.id}__** kisha kautume private./n Kumbuka bot haifany kaz kwa anonymous admin hutoweza kusearch/features nyingi huwezi tumia labda inline mode")
    chat_type = message.chat.type

    if chat_type == "private":
        try:
            cmd, group_id = message.text.split(" ", 1)
        except:
            await message.reply_text(
                "Samahan add hii bot kama admin kwenye group lako kisha tuma command hii <b>/niunge </b>kwenye group lako",
                quote=True
            )
            return

    elif chat_type in ["group", "supergroup"]:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (
            st.status != "administrator"
            and st.status != "creator"
            and str(userid) not in ADMINS
        ):
            await message.reply_text("lazima uwe  admin kwenye group hili!", quote=True)
            return
    except Exception as e:
        logger.exception(e)
        await message.reply_text(
            "Invalid Group ID!\n\nIf correct, Make sure I'm present in your group!!",
            quote=True,
        )

        return
    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == "administrator":
            ttl = await client.get_chat(group_id)
            title = ttl.title
            link = ttl.invite_link
            total = ttl.members_count
            addcon,user_id2 = await db.is_group_exist(str(group_id))
            if not addcon:
                await db.add_group(str(group_id),title,str(total) ,str(link),str(userid))
                await message.reply_text(
                    f"Sucessfully connected to **{title}**\n Sasa unaweza kuangalia maendeleo ya group lako kwa kutuma neno `group` ukiwa private!",
                    quote=True,
                    parse_mode="md"
                )
                if chat_type in ["group", "supergroup"]:
                    await client.send_message(
                        userid,
                        f"Asante kwa kutuamini umefanikiwa kuunganisha group \n **__{title}__** \n tutakupatia ofa  ya kila mteja atakae lipia kifurush kupitia grup lako kwa mara ya kwanza kupitia. \nUtapata tsh 1000 kwa kila mteja. kuona maendeleo ya group lako tuma neno `group' **tutakuwa tunakutumia ujumbe endapo mteja akilipa na Jinsi ya kupata mshiko wako**!",
                        parse_mode="md"
                    )
            elif user_id2 == userid :
                await message.reply_text(
                    "Samahan hili group tayar umeshaliunga kama unahitaj kulitoa tuma command /ondoa",
                    quote=True
                )
            else:
                await message.reply_text(
                    f"Samahan hili group tayar limeshaunganishwa na admin **{message.from_user.first_name}** Kama mnataka mabadiliko tafadhari mcheki msimiz wangu inbox @hrm45 ili awabadilishie!",
                    quote=True
                )
        else:
            await message.reply_text("Ni add admin kwenye group lako kisha jaribu tena", quote=True)
    except Exception as e:
        logger.exception(e)
        await message.reply_text('Kuna tatizo tafadhali jaribu badae!!!.', quote=True)
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
            ident, file_id = query.data.split(".dd#.")
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
                    await query.answer()
                    await client.send_cached_media(
                        chat_id=query.from_user.id,
                        file_id=file.file_id,
                        caption=f_caption
                    )
        elif query.data == "kenya":
            mkv = await client.ask(text = " Samahani sana wateja wetu wa Kenya bado hatuja weka utaratibu mzuri.\n  hivi karibun tutaweka mfumo mzuri ili muweze kupata huduma zetu", chat_id = query.from_user.id)
        
        elif query.data == "tanzania":
            mkv = await client.ask(text="** VIFURUSHI VYA SWAHILI GROUP** \n wiki 1(07 days) ➡️ 2000/= \n wiki 2(14 days) ➡️ 3000/= \n wiki 3(21 days) ➡️ 4000/= \n mwezi (30 days) ➡️ 5000/= \n\n Lipa kwenda **0624667219** halopesa:Ukishafanya malipo tuma screenshot ya muamala hapa kwenye hii bot .\n\n Ukimaliza subir kidogo ntakutaarifu endapo msimamiz wangu atamaliza kuhakiki muamala wako..\nPia kila muamala utakao lipia ofa zipo unaeza kuongezewa siku(1,2,3---)\n **__KARIBUN SANA SWAHILI GROUP__**", chat_id = query.from_user.id)
        

        
