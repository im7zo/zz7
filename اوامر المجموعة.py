from telethon import events 
from telethon .tl .functions .channels import EditBannedRequest 
from telethon .tl .types import ChatBannedRights 
from config import client 

ban_rights =ChatBannedRights (until_date =None ,view_messages =True )
restrict_rights =ChatBannedRights (until_date =None ,send_messages =True )
unban_rights =ChatBannedRights (until_date =None ,view_messages =False ,send_messages =False )

@client .on (events .NewMessage (outgoing =True ,pattern =r'\.(حظر|طرد|تقييد)'))
async def runkick (event ):
    await event .edit ("جارٍ تنفيذ الأمر...")
    command =event .pattern_match .group (1 )
    reply =await event .get_reply_message ()
    targetuser =None 

    try :
        if reply :
            targetuser =reply .sender_id 
        else :
            args =event .raw_text .split (" ",1 )
            if len (args )<2 :
                return await event .edit ("❗️يـجـب الـرد على رسـالة أو بـاليوزر أو بـالايدي")
            user_identifier =args [1 ].strip ().split ()[0 ]
            entity =await client .get_entity (user_identifier )
            targetuser =entity .id 

        user_rights =await client .get_permissions (event .chat_id ,targetuser )
        if user_rights .is_admin :
            return await event .edit ("⇜ لا يمكن تنفيذ الأمر على أدمن.")

        reason =""
        if "\n"in event .raw_text :
            reason =event .raw_text .split ("\n",1 )[1 ]

        if command =="طرد":
            await client .kick_participant (event .chat_id ,targetuser )
            action ="تم طرده"
        elif command =="حظر":
            await client (EditBannedRequest (event .chat_id ,targetuser ,ban_rights ))
            action ="تم حظره"
        elif command =="تقييد":
            await client (EditBannedRequest (event .chat_id ,targetuser ,restrict_rights ))
            action ="تم تقييده"

        entity =await client .get_entity (targetuser )
        mention =f"<a href='tg://user?id={entity.id}'>{entity.first_name}</a>"
        msg =f"{mention} {action}"
        if reason :
            msg +=f"\nسبب: {reason}"

        await client .send_message (event .chat_id ,msg ,parse_mode ="html")

    except Exception as e :
        await event .edit (f"حـدث خـطأ{e}")

    await event .delete ()

@client .on (events .NewMessage (outgoing =True ,pattern =r'\.(الغاء[_\s]?الحظر|الغاء[_\s]?التقييد|الغاء[_\s]?الطرد)'))
async def unrunkick (event ):
    await event .edit ("جارٍ تنفيذ الإلغاء...")
    command =event .pattern_match .group (1 ).replace ("_"," ").strip ()
    reply =await event .get_reply_message ()
    targetuser =None 

    try :
        if reply :
            targetuser =reply .sender_id 
        else :
            args =event .raw_text .split (maxsplit =1 )
            if len (args )<2 :
                return await event .edit ("❗️يـجـب الـرد على رسـالة أو بـاليوزر")
            user_identifier =args [1 ].strip ().split ()[0 ]
            entity =await client .get_entity (user_identifier )
            targetuser =entity .id 

        await client (EditBannedRequest (event .chat_id ,targetuser ,unban_rights ))

        entity =await client .get_entity (targetuser )
        mention =f"<a href='tg://user?id={entity.id}'>{entity.first_name}</a>"

        if "الحظر"in command or "الطرد"in command :
            action ="تم إلغاء حظره"
        else :
            action ="تم إلغاء تقييده"

        await client .send_message (event .chat_id ,f"{mention} {action}",parse_mode ="html")

    except Exception as e :
        await event .respond (f"⇜ حدث خطأ: {e}")

    await event .delete ()