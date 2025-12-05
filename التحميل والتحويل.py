import re
import asyncio
import json
import os
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import DeleteHistoryRequest
from config import client  # ← استيراد الكلينت من ملف محفوظ

DATA_DIR = "data"
LOAD_FILE = f"{DATA_DIR}/download_bot.json"

# -----------------------------
# إنشاء ملف البوت تلقائياً
# -----------------------------
def ensure_file():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(LOAD_FILE):
        with open(LOAD_FILE, "w", encoding="utf-8") as f:
            json.dump({"bot": "@aaazzjbot"}, f, ensure_ascii=False, indent=2)

# -----------------------------
# تحميل اسم البوت
# -----------------------------
def load_bot():
    ensure_file()
    with open(LOAD_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("bot", "@aaazzjbot")

# -----------------------------
# حفظ اسم البوت
# -----------------------------
def save_bot(bot_username):
    ensure_file()
    with open(LOAD_FILE, "w", encoding="utf-8") as f:
        json.dump({"bot": bot_username}, f, ensure_ascii=False, indent=2)

# البوت الحالي
def get_current_bot():
    return load_bot()


# ====================================================
#   🔄 تغيير بوت التحميل
# ====================================================
@client.on(events.NewMessage(outgoing=True, pattern=r"\.تغيير التحميل \+ (.+)$"))
async def change_download_bot(event):
    new_bot = event.pattern_match.group(1).strip()

    if not new_bot.startswith("@"):
        return await event.edit("يـرجى كتـابة اليوزر بـصيـغة @username")

    save_bot(new_bot)
    await event.edit(f"تـم تغـيير بـوت الـتحـميل إلـى\n**{new_bot}**")


# ====================================================
#   📥 أمر التحميل لجميع الوسائط
# ====================================================
@client.on(events.NewMessage(outgoing=True, pattern=r'\.حمل (.+)'))
async def download_media(event):
    download_bot = get_current_bot()
    chat = await event.get_chat()
    link = event.pattern_match.group(1).strip()
    message_to_delete = await event.edit("• انتظر جاري التحميل ...")

    try:
        async with client.conversation(download_bot) as conv:
            await conv.send_message(link)

            media_msgs = []
            timeout = 20
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    response = await conv.get_response()
                    await client.send_read_acknowledge(conv.chat_id)

                    # الاشتراك التلقائي بالقناة إذا طلب البوت
                    if "عليك الأشتراك" in response.message:
                        try:
                            channel_name = re.search(r"قناة البوت : (@\w+)", response.message).group(1)
                            await client(JoinChannelRequest(channel_name))
                            await conv.send_message(link)
                            continue
                        except Exception:
                            await event.edit("❗️ لم أتمكن من الاشتراك في القناة المطلوبة.")
                            return

                    if response.media:
                        media_msgs.append(response)

                except asyncio.TimeoutError:
                    break

            if media_msgs:
                for msg in media_msgs:
                    await client.send_file(chat, msg.media)
                await message_to_delete.delete()
                # حذف المحادثة مع البوت بعد التحميل
                try:
                    await client(DeleteHistoryRequest(peer=download_bot, max_id=0, just_clear=False, revoke=True))
                except Exception as e:
                    print(f"فشل حذف المحادثة: {e}")
            else:
                await event.edit("❗️المـحتوى غيـر موجـود أو لم يتـم الـرد فـي الوقـت المحـدد")

    except Exception as e:
        await event.edit(f"حـدث خـطأ أثنـاء التـحمـيل{e}")
        
async def handle_conversion (event ,command ,media_type ):
    chat =await event .get_chat ()
    reply_msg =await event .get_reply_message ()

    if not reply_msg :
        await event .edit ("يرجى الرد على ملصق/صورة/فيديو.")
        return 

    await event .edit ("يتم التحويل انتظر لطفا...")

    try :
        x =await client .forward_messages ('@Facnvbot',reply_msg )

        async with client .conversation ('@Facnvbot')as conv :
            converted_media =None 
            timeout =15 
            start_time =asyncio .get_event_loop ().time ()

            while asyncio .get_event_loop ().time ()-start_time <timeout :
                response =await conv .get_response (x .id )
                await client .send_read_acknowledge (conv .chat_id )

                if media_type =='sticker'and (response .sticker or response .video or response .document ):
                    converted_media =response 
                    break 
                elif media_type =='photo'and response .photo :
                    converted_media =response 
                    break 
                elif media_type =='audio'and response .audio :
                    converted_media =response 
                    break 

            if converted_media :
                await client .send_file (chat ,converted_media .media ,silent =True )
                await event .delete ()
                await asyncio .sleep (3 )
                await client (DeleteHistoryRequest (
                peer ='@Facnvbot',
                max_id =x .id ,
                just_clear =False ,
                revoke =True 
                ))
            else :
                await event .edit ("حـدث خـطأ أثنـاء التـحـويل")

    except Exception as e :
        print (e )
        await event .edit ("حدث خطأ أثناء التحويل.")

        # أوامر التحويل
@client .on (events .NewMessage (outgoing =True ,pattern =r'.صوره'))
async def sticker_to_photo (event ):
    await handle_conversion (event ,'.صوره','photo')

@client .on (events .NewMessage (outgoing =True ,pattern =r'.صوت'))
async def video_to_audio (event ):
    await handle_conversion (event ,'.صوت','audio')

@client .on (events .NewMessage (outgoing =True ,pattern =r'.ملصق'))
async def photo_to_sticker (event ):
    await handle_conversion (event ,'.ملصق','sticker')