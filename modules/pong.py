import telegram

def pongcb(bot,update):
    bot.sendMessage(update.message.chat_id,text="pong")

class pong:
    command = "ping"
    cb = pongcb
    args = False
