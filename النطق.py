from telethon import events 
from gtts import gTTS 
from os import remove 
from config import client # استيراد الكلاينت من ملف config.py

@client .on (events .NewMessage (outgoing =True ,pattern =r'\.انطق(?:\s+)?(\w+)?'))
async def run_tts (event ):
    await event .delete ()
    reply =await event .get_reply_message ()
    lang =event .pattern_match .group (1 )or "ar"
    filename ="Z-userbot.mp3"

    if not reply :
        return await event .edit ("❗يـجـب الـرد علـى رسـالة للـنطق")

    try :
        tts =gTTS (text =reply .message ,lang =lang ,slow =False )
        tts .save (filename )
        await client .send_file (event .chat_id ,filename )
    except Exception as e :
        await event .edit (f"❌ فشـل الـتحـويل{e}")
    finally :
        try :
            remove (filename )
        except :
            pass 