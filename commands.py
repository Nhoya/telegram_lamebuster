import re
from controls import _is_admin
from telegram.error import  *
def setctrl(bot,update,args):
    print(args[0])
    return
    if _is_admin(bot,update):
        global ban_time
        global max_messages
        message_id = update.message.message_id
        try:
            ctrl_option = re.search("\W\d+$", update.message.text)
            time = ctrl_option.group(0).strip()
            text_ = 'Filter set to *{0}* second(s) between messages'.format(time)
            max_time = time #change time
            bot.sendMessage(update.message.chat_id, text= text_, parse_mode='MARKDOWN', reply_to_message_id=message_id)
        except (AttributeError, IndexError) as e:
            bot.sendMessage(update.message.chat_id, text='Usage:\n`/setctrl time`',parse_mode='MARKDOWN', reply_to_message_id=message_id)

def setoption(bot,update,option,choices,bot_db):
    if _is_admin(bot,update):
        group_id = update.message.chat_id
        message_id = update.message.message_id
        try:
            target = re.search("\/.* (\D+)$", update.message.text).group(1)
            print (target)
            #choices e' un array
            if target in choices:
                bot_db.setGroupOption(group_id, option, target)
                bot.sendMessage(update.message.chat_id, text=option+" set to *"+target+"*",parse_mode='MARKDOWN', reply_to_message_id=message_id)
            else:
                raise AttributeError
        except (AttributeError, IndexError) as e:
                bot.sendMessage(update.message.chat_id, text='Usage:\n`/'+option+' '+' | '.join(choices)+'`',parse_mode='MARKDOWN', reply_to_message_id=message_id)

#WHITELIST COMMAND [SHOW | ADD | REMOVE]
def whitelist(bot,update,args,bot_db):
    group_id = update.message.chat_id
    if _is_admin(bot,update):
        message_body = update.message
        message_reply = message_body.reply_to_message
        whitelist = bot_db.getGroupWhitelist(group_id)
        message_id = message_body.message_id
        try:
            if args[0] == "show":
                whitelist_users = ""
                for elements in whitelist:
                    whitelist_users = whitelist_users+"\n"+elements['username']
                if whitelist_users:
                    bot.sendMessage(group_id,text="Whitelist:*"+whitelist_users+"*" ,parse_mode='MARKDOWN')
                else:
                    bot.sendMessage(group_id,text="Whitelist is empty")
                return
            user_name = message_reply.from_user.username
            user_id = message_reply.from_user.id
            _user={'username':user_name,'id':user_id}
            if message_reply.new_chat_member is not None:
                user_name = message_reply.new_chat_member.username
                user_id = message_reply.new_chat_member.id
                if re.search("\w*bot$",user_name) != None:
                    _user={'username':user_name,'id':user_id}
                else:
                    bot.sendMessage(group_id,text="Only bots can be whitelisted in this way")
                    return
            if args[0] == "add":
                if _user not in whitelist:
                    #ADD USER TO WHITELIST
                    bot_db.addToWhitelist(group_id,_user)
                    bot.sendMessage(group_id, text="*"+user_name+"* added to whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
                else:
                    bot.sendMessage(group_id, text="*"+user_name+"* already in whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
                print(whitelist)
            elif args[0] == "remove":
                if _user in whitelist:
                    #REMOVE USER FROM WHITELIST
                    bot_db.removeFromWhitelist(group_id,_user)
                    print(whitelist)
                    bot.sendMessage(group_id, text="*"+user_name+"* removed from whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
                else:
                    bot.sendMessage(group_id, text="User not in whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
            else:
                raise AttributeError
        except (AttributeError, IndexError) as e:
            print(e)
            bot.sendMessage(group_id, text="Usage:\n `/whitelist add |remove| show`",parse_mode='MARKDOWN', reply_to_message_id=message_id)

def unban(bot,update,bot_db):
    try:
        group_id = update.message.chat_id
        if _is_admin(bot,update):
            message_body = update.message
            message_reply = message_body.reply_to_message
            user_name = message_reply.from_user.username
            if user_name == "":
                user_name = "N/D"
            user_id = message_reply.from_user.id
            user = bot_db.getUser(group_id,user_id)
            _user={'username':user_name,'id':user_id}
            if _user in bot_db.getGroupBanlist(group_id):
                bot_db.removeBanned(group_id,_user)
                user['counter'] = 0
                bot.sendMessage(group_id,text="*"+user_name+"* Unbanned",parse_mode='MARKDOWN')
            else:
                bot.sendMessage(group_id,text="*"+user_name+"* Not in blacklist",parse_mode='MARKDOWN')
    except AttributeError:
        bot.sendMessage(group_id,text="Usage:\n `/unban quoting a message from the user you want to ban.`\n\nRemember:\n *you can't unban bots in that way* [Find Out     why](https://core.telegram.org/bots/faq#why-doesn-39t-my-bot-see-messages-from-other-bots)",parse_mode='MARKDOWN')

        

def banlist(bot,update,bot_db):
    if _is_admin(bot,update):
        group_id = update.message.chat_id
        banlist_users = ""
        banlist = bot_db.getGroupBanlist(group_id)
        print(banlist)
        for elements in banlist:
            banlist_users = banlist_users+"\n"+elements['username']
        if banlist_users:
            bot.sendMessage(group_id,text="Banlist:*"+banlist_users+"*" ,parse_mode='MARKDOWN')
        else:
            bot.sendMessage(group_id,text="Banlist is empty")

def ban(bot,update,bot_db, error):
    if _is_admin(bot,update):
        try:
            group_id = update.message.chat_id
            message_body = update.message
            message_reply = message_body.reply_to_message
            whitelist = bot_db.getGroupWhitelist(group_id)
            banlist = bot_db.getGroupBanlist(group_id)
            message_id = message_body.message_id
            user_name = message_reply.from_user.username
            print(user_name)
            if user_name == "":
                user_name = 'N/D'
            user_id = message_reply.from_user.id
            _role = bot.getChatMember(update.message.chat_id, message_reply.from_user.id)
            if _role.status == "administrator" or _role.status == "creator":
                bot.sendMessage(group_id,text="*You can't ban other admins stupid moron*",parse_mode='MARKDOWN')
                return
            _user={'username':user_name,'id':user_id}
            if _user not in banlist:
                bot_db.addBanned(group_id,_user)
                bot.kickChatMember(group_id, user_id)
                bot.sendMessage(group_id,text="*"+user_name+"* banned",parse_mode='MARKDOWN')
                if _user in whitelist:
                    bot_db.removeFromWhitelist(group_id,_user)
                    bot.sendMessage(group_id,text="*"+user_name+"* removed from whtelist",parse_mode='MARKDOWN')
            else:
                bot.sendMessage(group_id,text="*"+user_name+"* already in banlist",parse_mode='MARKDOWN')
        except AttributeError as e:
            bot.sendMessage(group_id,text="Usage:\n `/ban quoting a message from the user you want to ban.`\n\nRemember:\n *you can't ban bots in that way* [Find Out why](https://core.telegram.org/bots/faq#why-doesn-39t-my-bot-see-messages-from-other-bots)",parse_mode='MARKDOWN')
        except (TelegramError, BadRequest) as e:
            bot.sendMessage(group_id, text="I need Administrator rights")


#JUST FOR FUN
def pong(bot, update):
    bot.sendMessage(update.message.chat_id, text="pong")



