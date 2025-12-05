import random
import asyncio
import requests
from telethon import events
from config import client

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.قرآن$"))
async def send_quran(event):
    if not event.out:  # فقط الصادر منك
        return

    await asyncio.sleep(0.3)  # مهلة صغيرة حتى يختفي الأمر أسرع

    # احذف رسالة الأمر حتى يكون "صامت"
    try:
        await event.delete()
    except:
        pass

    ayah_number = random.randint(1, 6236)

    try:
        response = requests.get(
            f"http://api.alquran.cloud/v1/ayah/{ayah_number}/ar.abdulsamad"
        ).json()
    except:
        return  # صامت بدون أي إشعار

    if response.get("status") != "OK":
        return  # صامت أيضاً

    data = response["data"]
    text = data["text"]
    audio = data["audio"]
    surah_name = data["surah"]["name"]
    part = data["juz"]
    page = data["page"]
    hizb = data["hizbQuarter"]
    ayh = data["numberInSurah"]

    caption = f"""**「 {surah_name} 」**

⦓ {text} ⦔

- الجزء : ( {part} ) 
- الحزب : ( {hizb} ) 
- الأية : ( {ayh} ) 
- الصفحة : ( {page} )"""

    # إرسال الصوت والكليشة مباشرة بلا رد ولا تعديل
    await client.send_file(
        event.chat_id,
        audio,
        caption=caption,
        parse_mode="md"
    )