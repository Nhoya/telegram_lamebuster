import re
def _is_group(bot,update):
    chat_info = bot.get_chat(update.message.chat_id)
    if chat_info.type == "group" or chat_info.type == "supergroup":
        return True
    else:
        return False

def _is_admin(bot,update):
    group_id = update.message.chat_id
    _role = bot.getChatMember(update.message.chat_id, update.message.from_user.id)
    if _role.status == "administrator" or _role.status == "creator":
        return True
    else:
        return False

def check_join(bot, update, bot_db):
    group_id = update.message.chat_id
    join = update.message.new_chat_member
    _user = {'username':join.username,'id':join.id}
    print (_user)
    if join.id != bot.id:
        if re.search("\w*bot$",join.username) != None:
            if _user in bot_db.getGroupWhitelist(group_id):
                return
            bot.sendMessage(update.message.chat_id, text="Bot not in whitelist")
            bot.kickChatMember(group_id, join.id)
            return
        elif _user in bot_db.getGroupBanlist(group_id):
            bot.sendMessage(group_id, text='User in blacklist')
            bot.kickChatMember(group_id, join.id)
        return
        if join.id == bot.id:
            try:
                bot_db.getGroup(group_id)
            except GroupException as e:
            # bot is added to a group not in the whitelist
                bot.sendMessage(group_id, text=str(e) + " " + str(group_id))
                bot.leaveChat(group_id)
                return

