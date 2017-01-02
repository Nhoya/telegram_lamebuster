#!/usr/bin/env python3

from telegram import *
from telegram.ext import *
from time import *
import logging
import calendar
import re
import math

from config import TOKEN
from db import bot_database, GroupException, UserException
from controls import _is_group, _is_admin
from commands import setctrl, whitelist
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)

#vars
max_messages = 5 # messages limit
max_lease = 3.5 # seconds between successive messages
pardon = 0.2

bot_db = bot_database()

def handler(bot,update):
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

    try:
        whitelist = bot_db.getGroupWhitelist(group_id)
    except GroupException as e:
        bot.sendMessage(group_id, text=str(e) + " " + str(group_id))
        bot.leaveChat(group_id)
        return

    if _user in whitelist:
        return

    user = bot_db.getUser(group_id,user_id)

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
    print (timestamp, group_id, user_id, text, user['counter'])

    user['old_ts'] = timestamp
    user['last_msg'] = text

    #BAN MANAGEMENT
    if math.ceil(user['counter']) >= max_messages:
        #bot.kickChatMember(group_id,user_id)
        banned={'username':user_name,'id':user_id}
        if banned not in bot_db.getGroupBanlist(group_id):
            bot_db.addBanned(group_id,banned)
            bot.sendMessage(group_id, text='Triggered: User removed ' + str(user_id))
        user['counter'] = 0

def setfilter(bot,update):
    setoption(bot,update,'filter',['text','media','all'])

def _whitelist(bot,update,args):
    whitelist(bot,update,args,bot_db)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def check_bot(bot, update):
    group_id = update.message.chat_id
    join = update.message.new_chat_member
    _user = {'username':join.username,'id':join.id}
    print (_user)
    if join.id != bot.id:
        if re.search("\w*bot$",join.username) != None:
            # TODO: Check if the bot is in whitelist!!
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

def pong(bot, update):
    bot.sendMessage(update.message.chat_id, text="pong")

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
    dp.add_handler(CommandHandler("ping", pong))
    #dp.add_handler(CommandHandler("test", _is_group))
    dp.add_handler(CommandHandler("whitelist", _whitelist, pass_args=True))
    dp.add_handler(CommandHandler("setfilter",setfilter))
    dp.add_handler(CommandHandler("setctrl",setctrl, pass_args=True))
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
