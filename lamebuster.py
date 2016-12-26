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
message_num=0
max_messages=5

def _whitelist(bot,update):
    try:
        group_id = update.message.chat_id
        user_name = update.message.reply_to_message.from_user.username
        user_id = update.message.reply_to_message.from_user.id
        if update.message.text.split(' ')[1] == "add":
            bot.sendMessage(group_id, text="*"+user_name+"* added to whitelist",parse_mode='MARKDOWN')
            #ADD TO WHITELIST
        elif update.message.text.split(' ')[1] == "remove":
            bot.sendMessage(group_id, text="*"+user_name+"* removed from whitelist",parse_mode='MARKDOWN')
            #REMOVE FROM WHITELIST
        else:
            bot.sendMessage(group_id, text="Usage:\n `/whitelist add |remove`",parse_mode='MARKDOWN')
    except (IndexError, AttributeError) as e:
            bot.sendMessage(group_id, text="Usage:\n `/whitelist add |remove`",parse_mode='MARKDOWN')

def handler(bot,update):
    global message_num
    global max_messages
    
    #retriving info from message
    group_id = update.message.chat_id
    user_id = update.message.from_user.id
    timestamp = calendar.timegm(update.message.date.timetuple()) #datetime 2 timestamp
    message_num += 1
    
    
    #debug 
    #print (timestamp)
    #print (message_num)
    #print (user_id)
    #print (group_name)
    
    if message_num == max_messages:
        bot.kickChatMember(group_id,user_id)
        bot.sendMessage(group_id, text='User removed')

def setctrl(bot,update):
    global ban_time
    global max_messages
    try:
        ctrl_option = re.search("\W\d+$", update.message.text)
        time = ctrl_option.group(0).strip()
        text_ = 'Filter set to *{0}* second(s) between messages'.format(time)
        max_time = time #change time
        bot.sendMessage(update.message.chat_id, text= text_, parse_mode='MARKDOWN')
    except AttributeError as e:
        bot.sendMessage(update.message.chat_id, text='Usage:\n`/setctrl time`',parse_mode='MARKDOWN')
        

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def setfilter(bot,update):
    try:
        target = re.search("\W\D+$", update.message.text).group(1)
        print (target)
        bot.sendMessage(update.message.chat_id, text="Filter set to *"+target+"*",parse_mode='MARKDOWN')
    except AttributeError as e:
         bot.sendMessage(update.message.chat_id, text='Usage:\n`/filer text | media | all`',parse_mode='MARKDOWN')


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

