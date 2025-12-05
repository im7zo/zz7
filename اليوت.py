from config import client
from telethon import events
import asyncio
import re
import json
import os
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import DeleteHistoryRequest

DATA_DIR = "data"
YTB_FILE = f"{DATA_DIR}/youtube_bot.json"

# -----------------------------
# إنشاء ملف البوت تلقائياً
# -----------------------------
def ensure_file():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(YTB_FILE):
        with open(YTB_FILE, "w", encoding="utf-8") as f:
            json.dump({"bot": "@l_XI_ibot"}, f, ensure_ascii=False, indent=2)

# -----------------------------
# تحميل اسم البوت
# -----------------------------
def load_bot():
    ensure_file()
    with open(YTB_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("bot", "@l_XI_ibot")

# -----------------------------
# حفظ اسم البوت
# -----------------------------
def save_bot(bot_username):
    ensure_file()
    with open(YTB_FILE, "w", encoding="utf-8") as f:
        json.dump({"bot": bot_username}, f, ensure_ascii=False, indent=2)

# البوت الحالي
def get_current_bot():
    return load_bot()


# ====================================================
#   🔄 تغيير بوت اليوتيوب
# ====================================================
@client.on(events.NewMessage(outgoing=True, pattern=r"\.تغيير اليوت \+ (.+)$"))
async def change_yout_bot(event):
    new_bot = event.pattern_match.group(1).strip()

    if not new_bot.startswith("@"):
        return await event.edit("يـرجى كتـابة اليوزر بـصيـغة @username")

    save_bot(new_bot)
    await event.edit(f"تـم تغـيير بـوت اليـوتيوب إلـى\n**{new_bot}**")


# ====================================================
#   🎵 أمر اليوت — تحميل الصوت
# ====================================================
@client.on(events.NewMessage(outgoing=True, pattern=r'\.يوت (.+)'))
async def yt_audio(event):
    youtube_bot = get_current_bot()
    chat = event.chat_id
    query = event.pattern_match.group(1).strip()

    if query.startswith("."):
        query = query[1:]

    full_query = "يوت " + query
    await event.edit("• انتظر جاري البحث ...")

    try:
        async with client.conversation(youtube_bot) as conv:
            await conv.send_message(full_query)

            audio_clip = None
            timeout = 20
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    response = await conv.get_response()
                    await client.send_read_acknowledge(conv.chat_id)

                    if "عليك الأشتراك" in response.message:
                        try:
                            channel_name = re.search(r"قناة البوت : (@\w+)", response.message).group(1)
                            await client(JoinChannelRequest(channel_name))
                            await conv.send_message(full_query)
                            continue
                        except:
                            await event.edit("❗️ لم أتمكن من الاشتراك في القناة المطلوبة.")
                            return

                    if response.audio:
                        audio_clip = response
                        break

                except asyncio.TimeoutError:
                    break

        if audio_clip:
            await client.send_file(chat, file=audio_clip.media, silent=True)
            await event.delete()
        else:
            await event.edit("❗️المـحتوى غيـر موجـود أو لم يتـم الـرد فـي الوقـت المحـدد")

    except Exception as e:
        await event.edit(f"حـدث خـطأ أثنـاء التـحمـيل{e}")

    # حذف المحادثة مع البوت
    try:
        await client(DeleteHistoryRequest(peer=youtube_bot, max_id=0, just_clear=False, revoke=True))
    except Exception as e:
        print(f"فشل حذف المحادثة: {e}")