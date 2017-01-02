import re
from controls import _is_admin

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
#    global db
    if _is_admin(bot,update):
        group_id = update.message.chat_id
        message_id = update.message.message_id
        try:
            target = re.search("\/.* (\D+)$", update.message.text).group(1)
            print (target)
            #choices e' un array
            if target in choices:
                db[group_id][option] = target
                bot.sendMessage(update.message.chat_id, text=option+" set to *"+target+"*",parse_mode='MARKDOWN', reply_to_message_id=message_id)
            else:
                raise AttributeError
        except (AttributeError, IndexError) as e:
                bot.sendMessage(update.message.chat_id, text='Usage:\n`/'+option+' '+' | '.join(choices)+'`',parse_mode='MARKDOWN', reply_to_message_id=message_id)

def whitelist(bot,update,args,db):
#    global db
    group_id = update.message.chat_id
    if _is_admin(bot,update):
        if db[group_id].get('whitelist') == None:
            #CREATE WHITELIST
            db[group_id]['whitelist'] = []
        message_id = update.message.message_id
        if args[0] == "show":
            whitelist_users = ""
            for elements in db[group_id]['whitelist']:
                whitelist_users =whitelist_users+"\n"+elements['username']
                if whitelist_users:
                    bot.sendMessage(group_id,text="Whitelist:*"+whitelist_users+"*" ,parse_mode='MARKDOWN')
                else:
                    bot.sendMessage(group_id,text="Whitelist is empty")
                return
        try:
            user_name = update.message.reply_to_message.from_user.username
            user_id = update.message.reply_to_message.from_user.id
            _user={'username':user_name,'id':user_id}       
            if args[0] == "add":
                if _user not in db[group_id]['whitelist']:
                #ADD USER TO WHITELIST
                    db[group_id]['whitelist'].append(_user)
                    bot.sendMessage(group_id, text="*"+user_name+"* added to whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
                else:
                    bot.sendMessage(group_id, text="*"+user_name+"* already in whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
                print(db[group_id]['whitelist'])
            elif args[0] == "remove":
                if db[group_id].get('whitelist') == None:
                    bot.sendMessage(group_id, text="you should create a  whitelist first",parse_mode='MARKDOWN', reply_to_message_id=message_id)
                    return
                if _user in db[group_id]['whitelist']:
                    #REMOVE USER FROM WHITELIST
                    db[group_id]['whitelist'].remove(_user)
                    print(db[group_id]['whitelist'])
                    bot.sendMessage(group_id, text="*"+user_name+"* removed from whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
                else:
                    bot.sendMessage(group_id, text="User not in whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
            else:
                raise AttributeError
        except (AttributeError, IndexError) as e:
            bot.sendMessage(group_id, text="Usage:\n `/whitelist add |remove| show`",parse_mode='MARKDOWN', reply_to_message_id=message_id)

