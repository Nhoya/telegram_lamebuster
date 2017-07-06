import telegram
from modules.utils import isAdmin
from modules.dbmenage import SetupSession, BanUser, UnbanUser

def bancb(bot,update):
    uid = update.message.from_user.id
    gid = update.message.chat.id
    if not isAdmin(bot,uid,gid):
        return
    userid = update.message.reply_to_message.from_user.id
    if isAdmin(bot,userid,gid):
        bot.sendMessage(gid,text="You can't kick an administrator")
    else:
        db,cur = SetupSession()
        if BanUser(db,cur,userid,gid):
            #bot.kickChatMember(gid,userid)
            bot.sendMessage(gid,text="User wiped")
            db.close()
      

def unbancb(bot,update):
    uid = update.message.from_user.id
    gid = update.message.chat.id
    if not isAdmin(bot,uid,gid):
        return
    userid = update.message.reply_to_message.from_user.id
    if isAdmin(bot,userid,gid):
        #remove admin rights
        print("rimuovi poteri")
    else:
        db,cur = SetupSession()
        if UnbanUser(db,cur,userid,gid):
            #bot.unbanChatMember(gid,userid)
            bot.sendMessage(gid,text="Ban removed")
            db.close
class ban:
    command = "ban"
    cb = bancb
    args = False

class unban:
    command = "unban"
    cb = unbancb
    args = False
