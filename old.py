#!/usr/bin/env python3

from telegram import *
from telegram.ext import *
from time import *
import logging
import calendar
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)

#vars
TOKEN=''
max_messages = 5 # messages limit
max_lease = 2 # seconds between successive messages
group_whitelist = [-192014087]
db = {}

for g in group_whitelist:
	db[g] = {}

def handler(bot,update):
    global message_num
    global max_messages
    global users
    
    #retriving info from message
    group_id = update.message.chat_id
    user_id = update.message.from_user.id
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
	
    if user.get('counter') == None:
		#initialization
        user['counter'] = 0
        user['avg'] = 0
        user['old_ts'] = timestamp
    else:
		#user already exist
		lease = user['old_ts'] - timestamp
		if lease < max_lease:
    
    if user['counter'] >= 5:
		
    user['counter'] += 1
    
    #debug 
    print (group_id, user_id, timestamp)
    
    if db[group_id][user_id]['msg_num'] >= max_messages:
        #bot.kickChatMember(group_id,user_id)
        bot.sendMessage(group_id, text='Triggered: User removed ' + str(user_id))
        db[group_id][user_id]['msg_num'] = 0

def setctrl(bot,update):
    global ban_time
    global max_messages
    try:
        messages_time = re.search("\W\d+:\d+$", update.message.text)
        time = messages_time.group(0).split(':')[0].strip()
        messages = messages_time.group(0).split(':')[1]
        text_ = 'Filter set to {0} message(s) in {1} second(s)'.format(messages, time)
        max_messages = messages #change messages numbers
        max_time = time #change time
        bot.sendMessage(update.message.chat_id, text= text_)
    except AttributeError as e:
        bot.sendMessage(update.message.chat_id, text='Usage:\n`/setctrl time:messages`',parse_mode='MARKDOWN')
        

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
    #dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("setctrl",setctrl))
    dp.add_handler(MessageHandler(Filters.text, handler))

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



def setoption(bot,update,option,choices):
    global db
    if _is_admin(bot, update):
        group_id = update.message.chat_id
        try:
            target = re.search("\/.* (\D+)$", update.message.text).group(1)
            print (target)
            #choices e' un array
            if target in choices:
                db[group_id][option] = target
                bot.sendMessage(update.message.chat_id, text=option+" set to *"+target+"*",parse_mode='MARKDOWN')
            else:
                raise AttributeError
        except (AttributeError, IndexError) as e:
            choices.join('')
            bot.sendMessage(update.message.chat_id, text='Usage:\n`/'+option+' text | media | all`',parse_mode='MARKDOWN')


