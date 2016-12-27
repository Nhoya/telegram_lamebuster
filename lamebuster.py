#!/usr/bin/env python3

from telegram import *
from telegram.ext import *
from time import *
import logging
import calendar
import re
import math

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)

#vars
TOKEN=''
max_messages = 5 # messages limit
max_lease = 3.5 # seconds between successive messages
pardon = 0.2

group_whitelist = [-192014087]
db = {}

for g in group_whitelist:
	db[g] = {}

def _is_admin(bot,update):
    group_id = update.message.chat_id
    _role = bot.getChatMember(update.message.chat_id, update.message.from_user.id)
    if _role.status == "administrator" or _role.status == "creator":
        return True    

def _whitelist(bot,update):
    if _is_admin:
        message_id = update.message.message_id
        try:
            user_name = update.message.reply_to_message.from_user.username
            user_id = update.message.reply_to_message.from_user
            if update.message.text.split(' ')[1] == "add":
                bot.sendMessage(group_id, text="*"+user_name+"* added to whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
                #ADD TO WHITELIST
            elif update.message.text.split(' ')[1] == "remove":
                bot.sendMessage(group_id, text="*"+user_name+"* removed from whitelist",parse_mode='MARKDOWN', reply_to_message_id=message_id)
                #REMOVE FROM WHITELIST
            else:
                raise AttributeError
        except (IndexError, AttributeError) as e:
            bot.sendMessage(group_id, text="Usage:\n `/whitelist add |remove`",parse_mode='MARKDOWN', reply_to_message_id=message_id)

def handler(bot,update):
    global message_num
    global max_messages
    
    #retriving info from message
    group_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text
    timestamp = calendar.timegm(update.message.date.timetuple()) #datetime 2 timestamp
    
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
    
    if math.ceil(user['counter']) >= max_messages:
        #bot.kickChatMember(group_id,user_id)
        bot.sendMessage(group_id, text='Triggered: User removed ' + str(user_id))
        user['counter'] = 0

def setctrl(bot,update):
    if _is_admin:
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
    print (message_id)
    if _is_admin(bot, update):
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


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    #bot.GetUpdate()
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("whitelist", _whitelist))
    dp.add_handler(CommandHandler("setfilter",setfilter))
    dp.add_handler(CommandHandler("setctrl",setctrl))
    dp.add_handler(MessageHandler((Filters.text | Filters.sticker | Filters.command | Filters.photo), handler))
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

