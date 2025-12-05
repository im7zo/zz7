from telethon import events
import asyncio
from config import client

# حالات التفعيل/التعطيل
enabled_tasks = {
    "راتب": True,
    "بخشيش": True,
    "استثمار": False,
}

investment_amount = 1
tasks = {}

# دالة تنفيذ المهام
async def start_task(name, interval, message, chat_id):
    while enabled_tasks.get(name, False):
        try:
            await client.send_message(chat_id, message)
        except Exception as e:
            print(f"خطأ في المهمة {name}: {e}")
        await asyncio.sleep(interval)

# التحقق إذا المهمة تعمل مسبقًا
def is_running(name):
    return name in tasks and not tasks[name].done()

# ──────────────── أوامر المهام ────────────────

@client.on(events.NewMessage(pattern=r"\.راتب$"))
async def start_salary(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    chat_id = event.chat_id
    if not enabled_tasks["راتب"]:
        return await event.edit("تـم تـعطـيل أمـر الـراتـب")

    if is_running("راتب"):
        return await event.edit("الأمـر يعـمل بـالـفعل")

    await event.edit("بـدأ إرسـال **راتب** كُـل 10 دقـائق")
    tasks["راتب"] = asyncio.create_task(start_task("راتب", 600, "راتب", chat_id))


@client.on(events.NewMessage(pattern=r"\.بخشيش$"))
async def start_tip(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    chat_id = event.chat_id
    if not enabled_tasks["بخشيش"]:
        return await event.edit("تـم تـعطـيل أمـر الـبخـشيـش")

    if is_running("بخشيش"):
        return await event.edit("الأمـر يعـمل بـالـفعل")

    await event.edit("بـدأ إرسـال **بخشيش** كُـل 10 دقـائق")
    tasks["بخشيش"] = asyncio.create_task(start_task("بخشيش", 600, "بخشيش", chat_id))


@client.on(events.NewMessage(pattern=r"\.استثمار(?:\s+(\d+))?"))
async def start_invest(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    global investment_amount
    chat_id = event.chat_id
    num = event.pattern_match.group(1)

    if num:
        investment_amount = int(num)
        enabled_tasks["استثمار"] = True

        if is_running("استثمار"):
            tasks["استثمار"].cancel()

        await event.edit(f"بـدأ إرسـال **استثمار** {investment_amount} كُـل 20 دقـيقـة.")
        tasks["استثمار"] = asyncio.create_task(
            start_task("استثمار", 1200, f"استثمار {investment_amount}", chat_id)
        )

    else:
        return await event.edit("❗ استـخـدم الأمـر هكـذا:\n`.استثمار 500`")


# ──────────────── تعطيل المهام ────────────────

@client.on(events.NewMessage(pattern=r"\.تعطيل (.+)"))
async def disable_command(event):
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    target = event.pattern_match.group(1).strip()

    if target not in enabled_tasks:
        return await event.edit(" الأمـر غيـر صـحيـح تحـقق من الاسـم")

    enabled_tasks[target] = False

    if is_running(target):
        tasks[target].cancel()
        del tasks[target]

    await event.edit(f"تـم تـعطـيل **{target}** بـنجـاح")