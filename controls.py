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
