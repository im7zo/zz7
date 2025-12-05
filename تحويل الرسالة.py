from telethon import events 
import asyncio 
from config import client # استيراد الكلاينت من ملف config

@client .on (events .NewMessage (outgoing =True ,pattern =r'\.تحويل'))
async def tco1 (event ):
    reply =await event .get_reply_message ()
    if not reply :
        return await event .edit ("❗يـجـب الـرد علـى رسـالة")

    chat =await event .get_chat ()
    try :
        bot_entity =await client .get_entity ('@QuotLyBot')
        bot_chat_id =bot_entity .id 

        # إعادة توجيه الرسالة إلى البوت
        await client .forward_messages (bot_chat_id ,reply )

        await asyncio .sleep (5 )

        # استرجاع الرد من البوت
        async for message in client .iter_messages (bot_chat_id ,limit =5 ):
            if message .sticker :
                await client .send_message (chat ,file =message .sticker )

                await asyncio .sleep (3 )
                await client .delete_messages (chat ,[message .id ,reply .id ])
                break 
        else :
            await event .edit ("فـشـل تحـويل الرسـالة إلـى ملـصق")

            # حذف المحادثة مع البوت نهائيًا
        await client .delete_dialog (bot_chat_id )

    except asyncio .TimeoutError :
        return await event .edit ("❗لم يتـم الـرد فـي الوقـت المحـدد")
    except Exception as e :
        return await event .edit (f"حـدث خـطأ{e}")

    await event .delete ()