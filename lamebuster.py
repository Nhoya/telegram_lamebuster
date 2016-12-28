#!/usr/bin/env python3

from telegram import *
from telegram.ext import *
from time import *
import logging
import calendar
import re
import math

from config import TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)

#vars
max_messages = 5 # messages limit
max_lease = 3.5 # seconds between successive messages
pardon = 0.2

group_whitelist = [-192014087, -1001084538434 ]
db = {}
for g in group_whitelist:
	db[g] = {}

def _is_group(bot,update):
    chat_info = bot.get_chat(update.message.chat_id)
    if chat_info.type == "group" or chat_info.type == "supergroup":
        print(chat_info.type)
        return True
    else:
        return False

def _is_admin(bot,update):
    group_id = update.message.chat_id
    _role = bot.getChatMember(update.message.chat_id, update.message.from_user.id)
    if _role.status == "administrator" or _role.status == "creator":
        return True    

def _whitelist(bot,update):
    global db
    group_id = update.message.chat_id
    if _is_admin(bot,update):
        message_id = update.message.message_id
        try:
            user_name = update.message.reply_to_message.from_user.username
            user_id = update.message.reply_to_message.from_user.id
            _user={'username':user_name,'id':user_id}
            if update.message.text.split(' ')[1] == "add":
                if _user not in db[group_id]['whitelist']:
                    #ADD USER TO WHITELIST
                    db[group_id]['whitelist'].append(_user)
                    bot.sendMessage(group_id, text="*"+user_name+"* added to whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id) 
                else:
                    bot.sendMessage(group_id, text="*"+user_name+"* already in whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
                print(db[group_id]['whitelist'])
            
            elif update.message.text.split(' ')[1] == "remove":
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
        except (IndexError, AttributeError) as e:
            bot.sendMessage(group_id, text="Usage:\n `/whitelist add |remove`",parse_mode='MARKDOWN', reply_to_message_id=message_id)

def handler(bot,update):
    global db
    if _is_group(bot,update) is False:
        return
    global message_num
    global max_messages
    
    #retriving info from message
    group_id = update.message.chat_id
    user_id = update.message.from_user.id
    user_name= update.message.from_user.username
    text = update.message.text.encode('utf-8')
    timestamp = calendar.timegm(update.message.date.timetuple()) #datetime 2 timestamp
    _user = {'username':user_name,'id':user_id}
   
    if db[group_id].get('whitelist') == None:
        #CREATE WHITELIST
        db[group_id]['whitelist'] = []
         
    if _user in db[group_id]['whitelist']:
        return

    if db.get(group_id) == None:
		# bot is added to a group not in the whitelist
        bot.sendMessage(group_id, text='Group not in whitelist ' + str(group_id))
        bot.leaveChat(group_id)
        return
    group = db[group_id]
	
    if group.get(user_id) == None:
        group[user_id] = {}
    user = group[user_id]
    lease = 0
	
    if user.get('counter') == None:
		#initialization
        user['counter'] = 0
        user['old_ts'] = 0
        user['last_msg'] = ''
    else:
		#user already exist
        lease = timestamp - user['old_ts']
        if lease <= max_lease:
            if text == user['last_msg']:
                user['counter'] += user['counter']+1
            else:
                user['counter'] += 1
        else:
            if user['counter'] - pardon >= 0:
                user['counter'] -= pardon
                
            else:
                user['counter'] = 0
   
    user['counter'] = round(user['counter'], 2)
    
    #debug 
    print (timestamp, user_id, text, lease, user['counter'], text == user['last_msg'])
                 
    user['old_ts'] = timestamp
    user['last_msg'] = text
   #BAN MANAGEMENT 
    if math.ceil(user['counter']) >= max_messages:
        #bot.kickChatMember(group_id,user_id)
        banned={'username':user_name,'id':user_id}
        if db[group_id].get('banlist') == None:
            db[group_id]['banlist'] = []
        if banned not in db[group_id]['banlist']:
            db[group_id]['banlist'].append(banned)
            bot.sendMessage(group_id, text='Triggered: User removed ' + str(user_id))
        #debug
        print(db[group_id]['banlist'])
        user['counter'] = 0

def setctrl(bot,update):
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
 
def setfilter(bot,update):
    setoption(bot,update,'filter',['text','media','all'])


def setoption(bot,update,option,choices):
    global db
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

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def check_bot(bot, update):
    group_id = update.message.chat_id
    join = update.message.new_chat_member
    if join.id != bot.id:
        if re.search("\w*bot$",join.username) != None:
            bot.sendMessage(update.message.chat_id, text="Bot not in whitelist")
            bot.kickChatMember(group_id, join.id)
    if join.id == bot.id:
        if db.get(group_id) == None:
            # bot is added to a group not in the whitelist
            bot.sendMessage(group_id, text='Group not in whitelist ' + str(group_id))
            bot.leaveChat(group_id)
            return


class TestFilter(BaseFilter):
    def filter(self, message):
        return message.new_chat_member is not None

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    #bot.GetUpdate()
    dp = updater.dispatcher
    test_filter = TestFilter()
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("test", _is_group))
    dp.add_handler(CommandHandler("whitelist", _whitelist))
    dp.add_handler(CommandHandler("setfilter",setfilter))
    dp.add_handler(CommandHandler("setctrl",setctrl))
    dp.add_handler(MessageHandler((Filters.text | Filters.sticker | Filters.command | Filters.photo), handler))
    dp.add_handler(MessageHandler(test_filter, check_bot))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling(clean=True)

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

