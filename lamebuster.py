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
from controls import _is_group, _is_admin, check_join
from commands import setctrl, whitelist, pong, unban, banlist, ban
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)

#vars
max_messages = 5 # messages limit
max_lease = 3.5 # seconds between successive messages
pardon = 0.2
bot_db = bot_database()

def handler(bot,update):
    if _is_admin(bot,update):
        return
    if not _is_group(bot,update):
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

    if _user in bot_db.getGroupBanlist(group_id):
        bot.kickChatMember(group_id,user_id)
        return
    try:
        whitelist = bot_db.getGroupWhitelist(group_id)
    except GroupException as e:
        bot.sendMessage(group_id, text=str(e) + " " + str(group_id))
        bot.leaveChat(group_id)
        return

    if _user in whitelist:
        return

    user = bot_db.getUser(group_id,user_id)

    if re.search("(.{0,5}\n){4,}",text.decode('utf-8')) != None:
        user['counter'] += 5

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
            bot.sendMessage(group_id, text='User removed ' + str(user_id) +" "+ user_name)
        bot.kickChatMember(group_id,user_id)
        user['counter'] = 0

def setfilter(bot,update):
    setoption(bot,update,'filter',['text','media','all'])

def _whitelist(bot,update,args):
    whitelist(bot,update,args,bot_db)

def _check_join(bot,update):
    check_join(bot,update,bot_db)

def _banlist(bot,update):
    banlist(bot,update,bot_db)

def _unban(bot,update):
    unban(bot,update,bot_db)

def _ban(bot,update):
    ban(bot,update,bot_db)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

class OnjoinFilter(BaseFilter):
    def filter(self, message):
        return message.new_chat_member is not None


def test(bot,update):
    text= update.message.reply_to_message.new_chat_member
    print(text)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    #bot.GetUpdate()
    dp = updater.dispatcher
    OnJoin_filter = OnjoinFilter()
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("ping", pong))
    #dp.add_handler(CommandHandler("test", test))
    dp.add_handler(CommandHandler("whitelist", _whitelist, pass_args=True))
    dp.add_handler(CommandHandler("banlist", _banlist))
    dp.add_handler(CommandHandler("unban", _unban))
    dp.add_handler(CommandHandler("ban", _ban))
    dp.add_handler(CommandHandler("setfilter",setfilter))
    dp.add_handler(CommandHandler("setctrl",setctrl, pass_args=True))
    dp.add_handler(MessageHandler((Filters.text | Filters.sticker | Filters.command | Filters.photo |Filters.video |Filters.document), handler))
    dp.add_handler(MessageHandler(OnJoin_filter, _check_join))
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
