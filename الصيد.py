import asyncio
import random
import string
import time
from telethon import events
from telethon.tl.functions.channels import CreateChannelRequest, UpdateUsernameRequest
from telethon.tl.functions.account import CheckUsernameRequest
from config import client

# ==== متغيرات الصيد ====
is_hunting = False
hunt_task = None
hunt_info = {
    "started": False,
    "pattern": "",
    "results": [],
    "start_time": None,
    "continuous": False,
    "attempts": 0
}

# ==== توليد يوزر عشوائي حسب النمط ====
def generate_username(user_input: str) -> str:
    result = ""
    saved_char = None
    saved_digit = None
    saved_digit_for_3 = None
    previous_chars = set()
    previous_digits = set()

    for char in user_input:
        if char == "1":  # يولد حرف ثابت
            if saved_char is None:
                saved_char = random.choice(string.ascii_lowercase)
            result += saved_char

        elif char == "2":  # يولد رقم ثابت
            if saved_digit is None:
                saved_digit = random.choice(string.digits)
            result += saved_digit

        elif char == "3":  # يولد رقم ثابت مكرر خاص بالـ (3)
            if saved_digit_for_3 is None:
                saved_digit_for_3 = random.choice(string.digits)
            result += saved_digit_for_3

        elif char == "4":  # يولد حرف مختلف
            choices = [c for c in string.ascii_lowercase if c not in previous_chars]
            c = random.choice(choices) if choices else random.choice(string.ascii_lowercase)
            result += c
            previous_chars.add(c)

        elif char == "5":  # يولد رقم مختلف
            choices = [d for d in string.digits if d not in previous_digits]
            d = random.choice(choices) if choices else random.choice(string.digits)
            previous_digits.add(d)

        else:  # أي رمز ثاني يظل كما هو
            result += char

    return result

# ==== إنشاء قناة جديدة ====
async def create_channel():
    result = await client(CreateChannelRequest(
        title="• 𝐒𝐎𝐔𝐑𝐂𝐄 𝐙  𝐓𝐎𝐏 1",
        about="""By: @cfc_5
SOURCE Z TOP 1""",
        megagroup=False
    ))
    return result.chats[0]

# ==== تنفيذ الصيد ====
async def hunt_users(event, pattern, continuous=False):
    global is_hunting, hunt_task, hunt_info
    is_hunting = True
    hunt_info.update({
        "started": True,
        "pattern": pattern,
        "results": [],
        "start_time": time.time(),
        "continuous": continuous,
        "attempts": 0
    })

    await event.edit(f"تـم بــدء الصيـد علـى النمط: `{pattern}`")

    try:
        while is_hunting:
            username = generate_username(pattern)
            is_available = False
            try:
                is_available = await client(CheckUsernameRequest(username))
            except:
                pass

            hunt_info["attempts"] += 1

            if is_available:
                result = f"@{username}"
                hunt_info["results"].append(result)

                channel = await create_channel()
                try:
                    await client(UpdateUsernameRequest(channel, username))
                    await client.send_message(channel, f"• تـم صـيـد الـيوزر بنجاح: {result}")
                except:
                    await client.send_message(channel, f"❗ مـتاح ولـكـن فـشـل الـربـط {result}")

                if not continuous:
                    break

            await asyncio.sleep(1)

    except asyncio.CancelledError:
        pass

    if not continuous:
        await event.edit("تـم انتـهاء الصيـد.")
        is_hunting = False
        hunt_info["started"] = False

# ==== دالة التحقق من النمط ====
def validate_pattern(pattern: str) -> str:
    if any("\u0600" <= ch <= "\u06FF" for ch in pattern):
        return "❗  النمط غـيـر صـحـيح. لا يـمـكـن اسـتـخـدام الأحـرف العربية."
    if pattern[0] in ["2", "3" , "5" , "6" , "7" , "8" , "9" , "0"]:
        return "❗  النمط غـيـر صـحـيح. لا يـمـكـن ابـداء النمط بـرقـم."
    return None

# ==== أوامر الصيد (صادرة مني فقط) ====
@client.on(events.NewMessage(outgoing=True, pattern=r"\.صيد\s+(.+)"))
async def start_hunt_once(event):
    global hunt_task
    if is_hunting:
        await event.edit("❗ یـوجـد صـيـد جـارٍ حـالياً. أوقـفه بـاسـتخـدام `.ايقاف الصيد`")
        return

    pattern = event.pattern_match.group(1).strip()
    error_msg = validate_pattern(pattern)
    if error_msg:
        await event.edit(error_msg)
        return

    hunt_task = asyncio.create_task(hunt_users(event, pattern, continuous=False))

@client.on(events.NewMessage(outgoing=True, pattern=r"\.صيد_مستمر\s+(.+)"))
async def start_hunt_continuous(event):
    global hunt_task
    if is_hunting:
        await event.edit("❗ یـوجـد صـيـد جـارٍ حـالياً. أوقـفه بـاسـتخـدام `.ايقاف الصيد`")
        return

    pattern = event.pattern_match.group(1).strip()
    error_msg = validate_pattern(pattern)
    if error_msg:
        await event.edit(error_msg)
        return

    hunt_task = asyncio.create_task(hunt_users(event, pattern, continuous=True))

@client.on(events.NewMessage(outgoing=True, pattern=r"\.ايقاف الصيد"))
async def stop_hunt(event):
    global is_hunting, hunt_task, hunt_info
    if not is_hunting:
        await event.edit("❗ لا یـوجـد صـيـد جـارٍ.")
        return
    is_hunting = False
    if hunt_task:
        hunt_task.cancel()
    hunt_info["started"] = False
    await event.edit("تـم إيقـاف عـمـلـية الصـيـد.")

@client.on(events.NewMessage(outgoing=True, pattern=r"\.حالة الصيد"))
async def hunt_status(event):
    if not hunt_info["started"]:
        await event.edit("❗ لا تـوجد عـمـلية صـيـد شـغـالة حـالياً")
        return
    duration = int(time.time() - hunt_info["start_time"])
    count = len(hunt_info["results"])
    attempts = hunt_info["attempts"]
    msg = f"""تـم تـشـغـيل الصيـد.
النمط: {hunt_info['pattern']}
عـدد المحـاولـات: {attempts}
عـدد النتـائج: {count}
الوقت: {duration} ثـانـيـة
الـوضـع: {"مـسـتـمـر" if hunt_info["continuous"] else "مـرة واحـدة"}"""
    await event.edit(msg)