#!/usr/bin/env python3
TOKEN=''
from telegram import *
from telegram.ext import *
from time import *
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)

#vars
message_num=0

def handler(bot,update):
    global message_num
    
    #retriving info from message
    group_id = update.message.chat_id
    user_id = update.message.from_user.id
    message_num += 1
    
    #debug 
    #print (message_num)
    #print (user_id)
    #print (group_name)
    
    if message_num == 5:
        bot.kickChatMember(group_id,user_id)
        bot.sendMessage(group.id, text "User removed")
        

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
    dp.add_handler(MessageHandler(Filters.text, handler))
    #dp.add_handler(MessageHandler([Filters.photo],photo_handler))

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

