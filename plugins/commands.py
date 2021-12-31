import os
from plugins.channel import db
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from info import START_MSG, CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from utils import Media, get_file_details, get_size, save_file, get_filter_results,upload_photo
from pyrogram.errors import UserNotParticipant

@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot, message):
    """Show total files in database"""
    msg = await message.reply("Processing...⏳", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Saved files: {total}')
    except Exception as e:
        
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
    if reply and (reply.media or reply.photo):
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio","photo"):
        media = getattr(reply, file_type, None)
        if media is not None and reply.photo:
            name=await bot.ask(text = " send filename of the photo", chat_id = message.from_user.id)
            namee=name.text
            break
        elif media is not None:
            namee=media.file_name
    else:
        await msg.edit('This is not supported file format')
        return
    await msg.edit(f'Processing...⏳ file {namee} ')
    files = await get_filter_results(query=namee)
    if files and reply.photo:
        mime=await bot.ask(text = " send url of the photo", chat_id = message.from_user.id)
        mime=mime.text
        for file in files:
            if mime==file.file_ref:
                status =await  bot.ask(text = "send all to delete all files or send the video you want to delete on this movie/series ", chat_id = message.from_user.id)
                filez = await get_filter_results(query=file.file_id)
                if status.text == "all":
                    for fihj in filez:
                        result = await Media.collection.delete_one({
                            'file_id': fihj.file_id
                            })
                    result = await Media.collection.delete_one({
                        'mime_type': file.mime_type
                        })
                    
                elif not (status.photo | status.text):
                    for file_type in ("document", "video", "audio","photo"):
                        medi = getattr(status, file_type, None)
                        if medi is not None:
                            break
                    result = await Media.collection.delete_one({
                        'file_size': medi.file_size,
                        'mime_type': medi.mime_type
                        })
                    
    elif files:
        for file in files: 
            if file.file_size==media.file_size and file.mime_type == media.mime_type:
                result = await Media.collection.delete_one({
                    'file_size': media.file_size,
                    'mime_type': media.mime_type
                    }) 
                break  
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
            testi = await bot.ask(text = " send filename of the photo", chat_id = message.from_user.id)
            media.file_name = testi.text
            resv = ".dd#.x"
            mk=await bot.ask(text = " send artist or DJ or else send haijatafsiriwa", chat_id = message.from_user.id)
            access = await bot.ask(text = " send access and type eg m.t that is movie and access true or s.t series true", chat_id = message.from_user.id)
            link = await bot.ask(text = " send link", chat_id = message.from_user.id)
            media.file_name = f'{mk.text}.dd#.{media.file_name}{resv}.dd#.{access.text}.dd#.{link.text}'
            media.file_id , media.mime_type ,media.file_ref = await upload_photo(bot,reply)
            media.file_type = file_type
            media.caption = f'{reply.caption.html}\n🌟@Bandolako2bot \n💿[IMAGE URL]({media.file_ref)'if reply.caption else None
            break
        elif media is not None:
            testi = await bot.ask(text = " send filename of the document", chat_id = message.from_user.id)
            media.file_name = testi.text
            resv = ".dd#.x"
            mk=await bot.ask(text = " send artist or DJ or else send haijatafsiriwa", chat_id = message.from_user.id)
            media.file_name = f'{mk.text}.dd#.{media.file_name}{resv}'
            media.file_type = file_type
            media.caption = f'{reply.caption}\n🌟@Bandolako2bot 'if reply.caption else None
            break
    else:
        return
    replly,dta_id = await save_file(media)
    await mk.reply(f'{mk.text}\n caption {media.caption}\n type {media.file_type} \n {replly} with id {dta_id}')
   
@Client.on_message(filters.command('adddata') & filters.user(ADMINS))
async def add_data(bot, message):
    """Media Handler"""
    reply = message.reply_to_message
    pres = 'absent'
    if reply and reply.photo:
        msg = await reply.reply("Processing...⏳", quote=True)
        namee= await bot.ask(text = " send file name of the photo", chat_id = message.from_user.id)
        namee=namee.text
        files = await get_filter_results(query=namee)
        if files:
            mime = await bot.ask(text = " send photo link/URL for verifying", chat_id = message.from_user.id)
            for file in files: 
                title = file.mime_type
                if title==mime.text:
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
            mkv = await bot.ask(text = " send batch name season start with last ep separate by hash e.g 10#S01EP(1-10) or else m#movie", chat_id = message.from_user.id)
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
                    media.caption = f'{media.caption}\n🌟@Bandolako2bot 'if media.caption else None
                    media.file_name = f'{mkg}bnd2bot.dd#.H{mkv1}@.{resv}.d#.{mkv2}'
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
       
        await message.reply_text('Kuna tatizo tafadhali jaribu badae!!!.', quote=True)
        return
        
