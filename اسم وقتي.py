import asyncio
import random
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from datetime import datetime
import pytz
from config import client   # ← استخدام client من ملف خارجي

update_tasks = {}

time_formats = {
    "1": "𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟎",
    "2": "𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿𝟶",
    "3": "𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢",
    "4": "𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟬",
    "5": "𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿𝟶",
    "6": "۱۲۳۴۵۶۷۸۹۰",
    "7": "١٢٣٤٥٦٧٨٩٠",
    "8": "₁₂₃₄₅₆₇₈₉₀",
    "9": "⓵⓶⓷⓸⓹⓺⓻⓼⓽⓪",
    "10": "①②③④⑤⑥⑦⑧⑨⓪",
    "11": "𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡𝟘",
    "12": "❶❷❸❹❺❻❼❽❾⓿"
}

current_time_format = "1"

arabic_timezones = {
    "الإمارات": "Asia/Dubai",
    "البحرين": "Asia/Bahrain",
    "الجزائر": "Africa/Algiers",
    "جيبوتي": "Africa/Djibouti",
    "السعودية": "Asia/Riyadh",
    "السودان": "Africa/Khartoum",
    "الصومال": "Africa/Mogadishu",
    "العراق": "Asia/Baghdad",
    "عمان": "Asia/Muscat",
    "فلسطين": "Asia/Gaza",
    "قطر": "Asia/Qatar",
    "جزر القمر": "Indian/Comoro",
    "الكويت": "Asia/Kuwait",
    "لبنان": "Asia/Beirut",
    "ليبيا": "Africa/Tripoli",
    "مصر": "Africa/Cairo",
    "المغرب": "Africa/Casablanca",
    "موريتانيا": "Africa/Nouakchott",
    "اليمن": "Asia/Aden",
    "تونس": "Africa/Tunis",
    "الأردن": "Asia/Amman",
    "سوريا": "Asia/Damascus"
}

def format_time(time_obj):
    formatted_time = time_obj.strftime('%I:%M')
    original = "1234567890"
    fancy = time_formats[current_time_format]
    for i in range(10):
        formatted_time = formatted_time.replace(original[i], fancy[i])
    return formatted_time

# ======================================
#      🔥 تحديث الاسم الوقتي
# ======================================

async def update_name_periodically(event, user_name, timezone_str):
    chat_id = event.chat_id
    timezone = pytz.timezone(timezone_str)
    await event.delete()

    while update_tasks.get(chat_id, {}).get("name", False):
        now = datetime.now(timezone)
        formatted_time = format_time(now)

        try:
            await client(UpdateProfileRequest(last_name=formatted_time))
        except Exception as ex:
            print(f"خطأ تحديث الاسم: {str(ex)}")

        # 🔥 التوقف الفوري بدون انتظار دقيقة كاملة
        for _ in range(60):
            await asyncio.sleep(1)
            if not update_tasks.get(chat_id, {}).get("name", False):
                return


# ======================================
#      🔥 تحديث البايو الوقتي
# ======================================

async def update_bio_periodically(event, timezone_str, bios=None):
    chat_id = event.chat_id
    timezone = pytz.timezone(timezone_str)
    await event.delete()

    while update_tasks.get(chat_id, {}).get("bio", False):
        now = datetime.now(timezone)
        formatted_time = format_time(now)

        if bios:
            chosen = random.choice(bios)
            final_bio = f"{chosen} | {formatted_time}"
        else:
            final_bio = f"⌯ {formatted_time}"

        try:
            await client(UpdateProfileRequest(about=final_bio))
        except Exception as ex:
            print(f"خطأ تحديث البايو: {str(ex)}")

        # 🔥 التوقف الفوري
        for _ in range(60):
            await asyncio.sleep(1)
            if not update_tasks.get(chat_id, {}).get("bio", False):
                return


# ======================================
#       🟢 أوامر التشغيل
# ======================================

@client.on(events.NewMessage(pattern=r".اسم_وقتي (.+)", outgoing=True))
async def change_name_with_time(event):
    country = event.pattern_match.group(1)

    if country not in arabic_timezones:
        return await event.respond("**⌯ البلد غير موجود في القائمة.**")

    timezone_str = arabic_timezones[country]
    chat_id = event.chat_id

    update_tasks.setdefault(chat_id, {})["name"] = True
    me = await client.get_me()

    asyncio.ensure_future(update_name_periodically(event, me.first_name, timezone_str))


@client.on(events.NewMessage(pattern=r".بايو_وقتي (.+)", outgoing=True))
async def change_bio_with_time(event):
    country = event.pattern_match.group(1)

    if country not in arabic_timezones:
        return await event.respond("**⌯ البلد غير موجود في القائمة.**")

    timezone_str = arabic_timezones[country]
    chat_id = event.chat_id

    update_tasks.setdefault(chat_id, {})["bio"] = True

    bios = None
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.text:
            bios = [x.strip() for x in reply.text.splitlines() if x.strip()]

    asyncio.ensure_future(update_bio_periodically(event, timezone_str, bios))


# ======================================
#         🔴 أوامر الإيقاف
# ======================================

@client.on(events.NewMessage(pattern=r".ايقاف الاسم$", outgoing=True))
async def stop_name(event):
    chat_id = event.chat_id
    update_tasks.setdefault(chat_id, {})["name"] = False

    try:
        await client(UpdateProfileRequest(last_name=""))
        await event.respond("**⌯ تم إيقاف الاسم الوقتي بنجاح.**")
    except:
        pass

    await event.delete()


@client.on(events.NewMessage(pattern=r".ايقاف البايو$", outgoing=True))
async def stop_bio(event):
    chat_id = event.chat_id
    update_tasks.setdefault(chat_id, {})["bio"] = False

    try:
        await client(UpdateProfileRequest(about=""))
        await event.respond("**⌯ تم إيقاف البايو الوقتي بنجاح.**")
    except:
        pass

    await event.delete()


# ======================================
#     🟦 عرض وتغيير أشكال الوقت
# ======================================

@client.on(events.NewMessage(pattern=r"\.اشكال الوقت$", outgoing=True))
async def show_time_formats(event):
    txt = "\n".join([f"{k}: {v}" for k, v in time_formats.items()])
    await event.respond(f"**⌯ قائمة أشكال الوقت:**\n\n{txt}")
    await event.delete()


@client.on(events.NewMessage(pattern=r"\.الشكل (\d+)", outgoing=True))
async def change_time_format(event):
    global current_time_format
    key = event.pattern_match.group(1)

    if key in time_formats:
        current_time_format = key
        await event.respond(f"**⌯ تم تغيير شكل الوقت إلى {key}.**")
    else:
        await event.respond("**⌯ هذا الشكل غير موجود.**")

    await event.delete()