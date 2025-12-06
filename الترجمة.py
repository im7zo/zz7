from telethon import events
from googletrans import Translator
from config import client

translator = Translator()
auto_translate = False
translate_lang = "ar"  # اللغة الافتراضية

LANG_MAP = {
    "عربي": "ar", "العربية": "ar",
    "انكليزي": "en", "انجليزي": "en", "الانجليزية": "en", "الإنجليزية": "en",
    "فرنسي": "fr", "الفرنسية": "fr",
    "تركي": "tr", "التركية": "tr",
    "الماني": "de", "الألمانية": "de", "المانية": "de",
    "اسباني": "es", "الإسبانية": "es", "الاسبانية": "es",
    "روسي": "ru", "الروسية": "ru",
    "صيني": "zh-cn", "الصينية": "zh-cn",
}

# ==========================
# تفعيل الترجمة التلقائية
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الترجمة تفعيل$"))
async def enable_auto_translate(event):
    global auto_translate
    auto_translate = True
    await event.edit("تـم تـفعيل التـرجمة الفـورية")

# ==========================
# تعطيل الترجمة التلقائية
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الترجمة تعطيل$"))
async def disable_auto_translate(event):
    global auto_translate
    auto_translate = False
    await event.edit("تـم تعـطيل التـرجمة الفـورية")

# ==========================
# تغيير لغة الترجمة
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.لغة الترجمة (.+)$"))
async def change_language(event):
    global translate_lang
    lang = event.pattern_match.group(1).strip().lower()

    if lang in LANG_MAP:
        translate_lang = LANG_MAP[lang]
    else:
        if len(lang) <= 5:
            translate_lang = lang
        else:
            return await event.edit("اللـغة غـير مدعـومة جـرب لغة ثانـية")

    await event.edit(f"تـم تغيير لـغة الترجمة إلى `{translate_lang}` بـنجـاح ")

# ==========================
# تعديل الرسالة الصادرة وترجمتها
@client.on(events.NewMessage(outgoing=True))
async def auto_translate_handler(event):
    global auto_translate, translate_lang

    if not auto_translate:
        return

    text = event.raw_text
    if not text or len(text) < 1:
        return

    if text.startswith(".الترجمة") or text.startswith(".لغة الترجمة"):
        return

    try:
        # ✅ استخدم await إذا كانت مكتبتك async
        result = await translator.translate(text, dest=translate_lang)
        translated_text = result.text

        if translated_text.strip() != text.strip():
            await event.edit(translated_text)

    except Exception:
        pass