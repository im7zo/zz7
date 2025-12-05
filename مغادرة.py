from telethon import events 
from telethon .tl .functions .contacts import BlockRequest 
from telethon .tl .functions .channels import LeaveChannelRequest ,GetParticipantRequest 
from telethon .tl .types import User 
from config import client 
import os 


    # أمر تصفية وحظر البوتات
@client .on (events .NewMessage (pattern =r'^\.تصفيه البوتات$'))
async def clean_and_block_bots (event ):
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    removed =0 
    blocked =0 

    async for dialog in client .iter_dialogs ():
        user =dialog .entity 
        if isinstance (user ,User )and user .bot :
            try :
                await client .delete_dialog (user .id )
                removed +=1 
                await client (BlockRequest (user .id ))
                blocked +=1 
            except Exception :
                continue 

    await event .edit (f"تـم حـذف {removed} بـوت مـن المحادثات\nوتـم حـظر {blocked} بـوت بنـجاح.")

    # أمر مغادرة القنوات التي لست مشرفًا بها
@client .on (events .NewMessage (pattern =r'^\.مغادرة القنوات$'))
async def clean_and_block_bots (event ):
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    left =0 
    async for dialog in client .iter_dialogs ():
        if dialog .is_channel and getattr (dialog .entity ,'broadcast',False ):# قناة فقط
            try :
                participant =await client (GetParticipantRequest (dialog .entity ,'me'))
                # إذا لم تكن مشرف أو منشئ القناة
                if not (getattr (participant .participant ,'admin_rights',None )or getattr (participant .participant ,'creator',False )):
                    await client (LeaveChannelRequest (dialog .entity ))
                    left +=1 
            except Exception :
                continue 
    await event .edit (f"تـم مغـادرة القـنوات ← العدد: **{left}**")

    # أمر مغادرة الكروبات التي لست مشرفًا بها
@client .on (events .NewMessage (pattern =r'^\.مغادرة الكروبات$'))
async def clean_and_block_bots (event ):
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    left =0 
    async for dialog in client .iter_dialogs ():
        if dialog .is_channel and getattr (dialog .entity ,'megagroup',False ):# كروب فقط
            try :
                participant =await client (GetParticipantRequest (dialog .entity ,'me'))
                # إذا لم تكن مشرف أو منشئ الكروب
                if not (getattr (participant .participant ,'admin_rights',None )or getattr (participant .participant ,'creator',False )):
                    await client (LeaveChannelRequest (dialog .entity ))
                    left +=1 
            except Exception :
                continue 
    await event .edit (f"تـم مغـادرة الكـروبـات ← العدد: **{left}**")